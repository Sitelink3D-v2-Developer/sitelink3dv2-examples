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
 
    # First we determine whether this site is localised. If so, the result will also contain the transform
    # version that we will later provide to the transform service in order to convert from local grid (nee) to geodetic (wgs84) space.
    localised, transform_revision = get_current_site_localisation(a_server=server, a_site_id=args.site_id, a_headers=headers)
   
    if localised:

        # Now we have a localisation version, we can ask the transform service for an approximation matrix and use that
        # to transform our local grid points into cartesian points. These two steps are done in the block below using 
        # the get_local_grid_to_cartesian_approx_matrix and local_grid_to_cartesian functions.
        logging.info("Querying transform service for local points in file {}.".format(args.transform_local_position_points_file))
        
        with open(args.transform_local_position_points_file, "r") as points_file:
            points = json.loads(points_file.read())

            # Write the converted geodetic (WGS84) coordinates to an output file in a directory named for this site.
            approx_matrices, point_index_to_voxel_index = get_approx_matrices(a_voxel_extent=600, a_local_points=points, a_transform_revision=transform_revision, a_site_id=args.site_id, a_server=server, a_headers=headers)
            
            cartesian_coords = local_grid_to_cartesian(points, approx_matrices, point_index_to_voxel_index)

            # Write the converted cartesian (ECEF) coordinates to an output file in a directory named for this site.
            output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
            with open(os.path.join(output_dir, "coords.cartesian.json"), "w") as out_coords_file:
                out_coords_file.write(json.dumps(cartesian_coords,sort_keys=True,indent=4))

            # Lastly we convert the cartesian coordinates into geodetic coordinates. Below converts to WGS84.
            wgs84_coords = cartesian_to_wgs84(a_cartesian_coords=cartesian_coords)
            
            with open(os.path.join(output_dir, "coords.wgs84.json"), "w") as wgs84_coords_file:
                wgs84_coords_file.write(json.dumps(wgs84_coords,sort_keys=True,indent=4))

    else:
        logging.info("Site not localised.")

if __name__ == "__main__":
    main()    
