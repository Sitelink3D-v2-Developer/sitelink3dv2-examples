import math
import base64
import json
import requests
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["file_download", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def get_local_grid_to_cartesian_approx_matrix(a_server_url, a_headers, a_site_id, a_transform_rev, a_voxel_extent, a_voxel_list):
   
    transform_url = "{0}/transform/v1/site/{1}/transform_rev/{2}/enz_to_ecef_approx_matrix".format(a_server_url, a_site_id, a_transform_rev)

    return session.post(transform_url, headers=a_headers, data=json.dumps({
        "voxel_extent": a_voxel_extent,
        "voxels": a_voxel_list,
    }))

def get_approx_matrices(a_voxel_extent, a_local_points, a_transform_revision, a_site_id, a_server, a_headers):

    voxel_list = []
    point_index_to_voxel_index = []
    voxel_hash_to_voxel_list_index = {}

    # Determine the unique voxels we require matrices for to avoid asking for duplicates where multiple points fall within the same voxel.

    for i, point in enumerate(a_local_points):

        voxel ={
            "i": int(point["e"] / a_voxel_extent),
            "j": int(point["n"] / a_voxel_extent),
            "k": int(point["z"] / a_voxel_extent),
        }
        voxel_hash = json.dumps(voxel,sort_keys=True)

        voxel_list_index = None
        if voxel_hash not in voxel_hash_to_voxel_list_index:
            voxel_list_index = len(voxel_list)
            voxel_list.append(voxel)
            voxel_hash_to_voxel_list_index[voxel_hash] = voxel_list_index
        else:
            voxel_list_index = voxel_hash_to_voxel_list_index[voxel_hash]

        point_index_to_voxel_index.append(voxel_list_index)
        
    approx_matrix_response = get_local_grid_to_cartesian_approx_matrix(a_server.to_url(), a_headers, a_site_id, a_transform_revision, a_voxel_extent, voxel_list)
    approx_matrices = approx_matrix_response.json()["matrices"]

    return approx_matrices, point_index_to_voxel_index

def cartesian_to_wgs84(a_cartesian_coords):

    Wgs84Spheroid = Spheroid(a_semi_major_axis=6378137.0, a_flattening=1.0 / 298.257223563)
    wgs84_coords = []
    for coord in a_cartesian_coords:
        geodetic = Wgs84Spheroid.cartesianToGeodetic(coord)
        wgs84_coords.append(geodetic)

    return wgs84_coords


def GetTransform(a_server, a_site_id, a_headers):
    start=["transform_gc3"] 
    end=["transform_gc3", None]
    rdm_url = "{}/rdm/v1/site/{}/domain/sitelink/view/_head?limit=500".format(a_server.to_url(), a_site_id)
    params={}
    params["start"] = base64.urlsafe_b64encode(json.dumps(start).encode('utf-8')).decode('utf-8').rstrip("=")
    params["end"] = base64.urlsafe_b64encode(json.dumps(end).encode('utf-8')).decode('utf-8').rstrip("=")
    response = session.get(rdm_url, headers=a_headers, params=params)
    rdm_view_list = response.json()
    return rdm_view_list

# Determine whether this site is localised by searching for an RDM object with id "transform_gc3". This is
# achieved by querying the _head of RDM rather than relying on a specific RDM view. If localised, also return 
# the localisation revision
def get_current_site_localisation(a_server, a_site_id, a_headers):
    rdm_view_list = GetTransform(a_server=a_server, a_site_id=a_site_id, a_headers=a_headers)

    localised = False
    transform_revision = ""
    for obj in rdm_view_list["items"]:
        try:
            if obj["id"] == "transform_gc3":
                localised = True
                transform_revision = obj["value"]["_rev"]
                logging.info("Found current site localisation file {} (version {})".format(obj["value"]["file"]["name"],transform_revision))
                break
        except KeyError:
            continue
    return localised, transform_revision

def wgs84_coord_to_object_list_item(a_wgs_point):
    obj = {
        "items" : []
    }
    if bool(a_wgs_point):

        try:
            lat = a_wgs_point["lat"]
            item_lat = {
                    "title" : "latitude",
                    "value" : lat
                }
            obj["items"].append(item_lat)
        except KeyError:
            pass

        try:
            lon = a_wgs_point["lon"]
            item_lon = {
                    "title" : "longitude",
                    "value" : lon
                }
            obj["items"].append(item_lon)
        except KeyError:
            pass

        item_dir = {
                "title" : "direction"
            }
        try:
            dir = a_wgs_point["dir"]
            item_dir["value"] = dir           
        except KeyError:
            item_dir["value"] = "-"     
        obj["items"].append(item_dir)

        try:
            alt = a_wgs_point["alt"]
            item_alt = {
                    "title" : "altitude",
                    "value" : alt
                }
            obj["items"].append(item_alt)
        except KeyError:
            pass

        try:
            alt = a_wgs_point["height"]
            item_alt = {
                    "title" : "altitude",
                    "value" : alt
                }
            obj["items"].append(item_alt)
        except KeyError:
            pass

    return obj    

# Cache local points and transform information to facilitate batch processing of conversions
# This class handles the management of storing localized coordinates that are typically processed
# one at a time or line by line. Calling code can use TransformManager to determine approximation
# matrices for a batch of points and return a converted WGS84 list in one go as if they had been
# converted one point at a time. This improves the performance of calling code.
#
# The transformation of aggregated points also accommodates the transition from one transform revision
# to another seamlessly.
class TransformManager():
    def __init__(self): 
        self.m_local_machine_point_dict = {} # keyed on transform revision appropriate to the contained points

    def addLocalPoint(self, a_point, a_line_index, transform_info):
        if not transform_info["revision"] in self.m_local_machine_point_dict:
            point_list_json = {
                "point_list" : [],
                "index_list" : []
            }
            self.m_local_machine_point_dict[transform_info["revision"]] = point_list_json
        self.m_local_machine_point_dict[transform_info["revision"]]["point_list"].append(a_point)
        self.m_local_machine_point_dict[transform_info["revision"]]["index_list"].append(a_line_index)

    def transform(self, a_server, a_site_id, a_headers):
        output_list = []
        for transform_revision in self.m_local_machine_point_dict.keys():
            point_list_to_transform = self.m_local_machine_point_dict[transform_revision]["point_list"]
            logging.debug("Transforming {} points recorded during transform revision {}".format(len(point_list_to_transform), transform_revision))
            approx_matrices, point_index_to_voxel_index = get_approx_matrices(a_voxel_extent=600, a_local_points=point_list_to_transform, a_transform_revision=transform_revision, a_site_id=a_site_id, a_server=a_server, a_headers=a_headers)
        
            cartesian_coords = local_grid_to_cartesian(point_list_to_transform, approx_matrices, point_index_to_voxel_index)

            # Lastly we convert the cartesian (ECEF) coordinates into geodetic coordinates. Below converts to WGS84.
            wgs84_points = cartesian_to_wgs84(a_cartesian_coords=cartesian_coords)
            object_list = []
            for i, point in enumerate(wgs84_points):
                object_list.append( {
                            "object" : wgs84_coord_to_object_list_item(a_wgs_point=point),
                            "list_index" : self.m_local_machine_point_dict[transform_revision]["index_list"][i]
                        }
                    )
            output_list.extend(object_list)
            
        return output_list

# This class abstracts the collation of WGS84 points natively provided by connected clients and those
# that are the result of transformation. For efficiency, the transformation is performed once which 
# means that "local" and "geodetic" coordinates are stored separately by the use of the "add_local_point"
# and "add_geodetic_point" functions respecitvely. To preserve point ordering, local points are added
# to a list that is transformed by calculate_geodetic_points but placeholders for these local points are
# added to m_geodetic_coordinate_list so that the transformed local points can be substitued into the 
# correct position (index) when available. 
class GeodeticCoordinateManager():
    def __init__(self):
        self.m_geodetic_coordinate_list = []
        self.m_transform_manager = TransformManager()

    def add_geodetic_point(self, a_point):
        self.m_geodetic_coordinate_list.append(a_point)

    def add_local_point(self, a_point, transform_info):
        next_geodetic_coordinate_list_index = len(self.m_geodetic_coordinate_list)
        self.m_geodetic_coordinate_list.append(None)
        self.m_transform_manager.addLocalPoint(a_point, next_geodetic_coordinate_list_index, transform_info)

    def calculate_geodetic_points(self, a_server, a_site_id, a_headers):
        # return the contiguous list of geodetic points, first by submitting the local points for transformation via
        # the member transformation manager, then by submitting the returned transformed coordinates back into their
        # spot in the geodetic list using the index tracking used when the local points were cached.
        transformed_point_list = self.m_transform_manager.transform(a_server, a_site_id, a_headers)

        for point in transformed_point_list:
            self.m_geodetic_coordinate_list[point["list_index"]] = point["object"]

        return self.m_geodetic_coordinate_list


class Spheroid():
    def __init__(self, a_semi_major_axis, a_flattening):
        # Defined constants
        self.m_semi_major_axis = a_semi_major_axis
        self.m_flattening = a_flattening
        # Derived constants
        self.m_semi_minor_axis = self.m_semi_major_axis * (1.0 - self.m_flattening)
        self.m_semi_major_axis_squared = math.pow(self.m_semi_major_axis, 2)
        self.m_semi_minor_axis_squared = math.pow(self.m_semi_minor_axis, 2)
        self.m_first_eccentricity = math.sqrt((self.m_semi_major_axis_squared - self.m_semi_minor_axis_squared) / self.m_semi_major_axis_squared)
        self.m_first_eccentricity_squared = math.pow(self.m_first_eccentricity, 2)
        self.m_second_eccentricity = math.sqrt((self.m_semi_major_axis_squared - self.m_semi_minor_axis_squared) / self.m_semi_minor_axis_squared)
        self.m_second_eccentricity_squared = math.pow(self.m_second_eccentricity, 2)

    def cartesianToGeodetic(self, a_point):
        x = a_point["x"]
        y = a_point["y"]
        z = a_point["z"]

        longitude = math.atan2(y, x)

        x_squared = math.pow(x, 2)
        y_squared = math.pow(y, 2)

        p = math.sqrt(x_squared + y_squared)
        psi = math.atan2(z * self.m_semi_major_axis, p * self.m_semi_minor_axis)
        sin_psi = math.sin(psi)
        cos_psi = math.cos(psi)

        latitude = math.atan2(
                z + self.m_second_eccentricity_squared * self.m_semi_minor_axis * math.pow(sin_psi, 3),
                p - self.m_first_eccentricity_squared * self.m_semi_major_axis * math.pow(cos_psi, 3))

        sin_latitude = math.sin(latitude)
        sin_squared_latitude = math.pow(sin_latitude, 2)
        v = self.m_semi_major_axis / math.sqrt(1.0 - self.m_first_eccentricity_squared * sin_squared_latitude)

        height = math.sqrt(x_squared + y_squared + math.pow(z + v * self.m_first_eccentricity_squared * sin_latitude, 2)) - v

        return { 
            "lon": math.degrees(longitude), 
            "lat": math.degrees(latitude), 
            "height": height
        }

def local_grid_to_cartesian(points, approx_matrices, point_index_to_matrix_index):

    coords = []
    for i in range(len(points)):
        approx_matrix = approx_matrices[point_index_to_matrix_index[i]]
        point = points[i]
        coords.append({
            "x": approx_matrix["rows"][0][0] * point["e"] +
                approx_matrix["rows"][0][1] * point["n"] +
                approx_matrix["rows"][0][2] * point["z"] +
                approx_matrix["rows"][0][3],
            "y": approx_matrix["rows"][1][0] * point["e"] +
                approx_matrix["rows"][1][1] * point["n"] +
                approx_matrix["rows"][1][2] * point["z"] +
                approx_matrix["rows"][1][3],
            "z": approx_matrix["rows"][2][0] * point["e"] +
                approx_matrix["rows"][2][1] * point["n"] +
                approx_matrix["rows"][2][2] * point["z"] +
                approx_matrix["rows"][2][3],
        })
    return coords

def query_and_download_site_localization_file_history(a_server_config, a_site_id, a_headers, a_target_dir):
    page_traits = RdmViewPaginationTraits(a_page_size="500", a_start=["transform_gc3"], a_end=["transform_gc3",None])     
    ret = query_rdm_by_domain_view(a_server_config=a_server_config, a_site_id=a_site_id, a_domain="sitelink", a_view="_hist", a_headers=a_headers, a_params=page_traits.params())

    logging.info("{} localization objects have been used at this site.".format(len(ret["items"])))
    for loc in ret["items"]:
        file_description = "transform file effective from timestamp {}".format(loc["value"]["_at"])
        logging.info("Downloading {}".format(file_description))
        target_dir = os.path.join(a_target_dir, file_description)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "metadata.json"),"w") as metadata_file:
            metadata_file.write(json.dumps(loc["value"], indent=4))
        download_file(a_server_config=a_server_config, a_site_id=a_site_id, a_file_uuid=loc["value"]["file"]["uuid"], a_headers=a_headers, a_target_dir=target_dir, a_target_name=loc["value"]["file"]["name"])

        for other_file in loc["value"]["other_files"]:
            download_file(a_server_config=a_server_config, a_site_id=a_site_id, a_file_uuid=other_file["uuid"], a_headers=a_headers, a_target_dir=target_dir, a_target_name=other_file["name"])

    return ret["items"]

def get_transform_info_for_time(a_ms_since_epoch, a_transform_list):

    transform_info = {}
    for transform in a_transform_list:
        if a_ms_since_epoch >= transform["value"]["_at"]:
            transform_info["revision"] = transform["value"]["_rev"]
            transform_info["file_name"] = transform["value"]["file"]["name"]
        else:
            break
    return transform_info