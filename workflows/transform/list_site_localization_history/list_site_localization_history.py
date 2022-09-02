#!/usr/bin/python
import logging
import os
import sys
import json
import base64

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "file_download", "rdm_pagination_traits", "rdm_list", "transform", "site_detail"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()


def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id] )
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    # >> Authorization
    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    # << Authorization

    # First we determine whether this site is localised. If so, the result will also contain the transform
    # version that we will later provide to the transform service in order to convert from local grid (nee) to geodetic (wgs84) space.
    localised, transform_revision = get_current_site_localisation(a_server=server, a_site_id=args.site_id, a_headers=headers)
    
    if localised:

        output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

        # Query and download all versions of the localization history at this site to a directory named as a function of the time the file was the active localization.
        query_and_download_site_localization_file_history(a_server_config=server, a_site_id=args.site_id, a_headers=headers, a_target_dir=output_dir)

    else:
        logging.info("Site not localized.")

if __name__ == "__main__":
    main()    
