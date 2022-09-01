#!/usr/bin/python
import logging
import os
import sys
import json
import base64

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_list", "transform", "site_detail"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()


def get_local_grid_to_cartesian_approx_matrix(a_server_url, a_headers, a_site_id, a_transform_rev, a_voxel_extent, a_voxel_list):
   
    transform_url = "{0}/transform/v1/site/{1}/transform_rev/{2}/enz_to_ecef_approx_matrix".format(a_server_url, a_site_id, a_transform_rev)

    return session.post(transform_url, headers=a_headers, data=json.dumps({
        "voxel_extent": a_voxel_extent,
        "voxels": a_voxel_list,
    }))



def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_transform_local_position_points_file] )
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
 
    # First we determine whether this site is localised by searching for an RDM object with id "transform_gc3". This is
    # achieved by querying the _head of RDM rather than relying on a specific RDM view. The result will also contain the transform
    # version that we will later provide to the transform service in order to convert from local grid (nee) to geodetic (wgs84) space.
    
    # We ask RDM for only the object with id of "transform_gc3" with the following start and end parameters
    rdm_view_list = GetTransform(a_server=server, a_site_id=args.site_id, a_headers=headers)

    localised = False
    transform_revision = ""
    for obj in rdm_view_list["items"]:
        try:
            if obj["id"] == "transform_gc3":
                localised = True
                transform_revision = obj["value"]["_rev"]
                logging.info("Found site localisation (version {})".format(transform_revision))
                break
        except KeyError:
            continue
    
    if localised:

        # Now we have a localisation version, we can ask the transform service for an approximation matrix and use that
        # to transform our local grid points into cartesian points. These two steps are done in the block below using 
        # the get_local_grid_to_cartesian_approx_matrix and local_grid_to_cartesian functions.
        logging.info("Querying transform service for local points in file {}.".format(args.transform_local_position_points_file))
        
        voxel_extent = 600.0
        
        with open(args.transform_local_position_points_file, "r") as points_file:
            points = json.loads(points_file.read())

            voxel_list = []
            point_index_to_voxel_index = []
            voxel_hash_to_voxel_list_index = {}

            # Determine the unique voxels we require matrices for to avoid asking for duplicates where multiple points 
            # fall within the same voxel.

            for i, point in enumerate(points):

                voxel ={
                    "i": int(point["e"] / voxel_extent),
                    "j": int(point["n"] / voxel_extent),
                    "k": int(point["z"] / voxel_extent),
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
                
            approx_matrix_response = get_local_grid_to_cartesian_approx_matrix(server.to_url(), headers, args.site_id, transform_revision, voxel_extent, voxel_list)
            approx_matrices = approx_matrix_response.json()["matrices"]

            coords = local_grid_to_cartesian(points, approx_matrices, point_index_to_voxel_index)

            output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

            # Write the converted cartesian (ECEF) coordinates to an output file in a directory named for this site.
            with open(os.path.join(output_dir, "coords.cartesian.json"), "w") as out_coords_file:
                out_coords_file.write(json.dumps(coords,sort_keys=True,indent=4))

            # Lastly we convert the cartesian coordinates into geodetic coordinates. Below converts to WGS84.
            Wgs84Spheroid = Spheroid(a_semi_major_axis=6378137.0, a_flattening=1.0 / 298.257223563)
            wgs84_coords = []
            for coord in coords:
                geodetic = Wgs84Spheroid.cartesianToGeodetic(coord)
                wgs84_coords.append(geodetic)

            # Write the converted geodetic (WGS84) coordinates to an output file in a directory named for this site.
            with open(os.path.join(output_dir, "coords.wgs84.json"), "w") as wgs84_coords_file:
                wgs84_coords_file.write(json.dumps(wgs84_coords,sort_keys=True,indent=4))

    else:
        logging.info("Site not localised.")

if __name__ == "__main__":
    main()    
