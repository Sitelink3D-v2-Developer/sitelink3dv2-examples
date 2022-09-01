import math
import base64
import json
import requests

session = requests.Session()

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
