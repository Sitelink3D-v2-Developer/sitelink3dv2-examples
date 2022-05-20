#!/usr/bin/python

import logging
import os
import sys
from textwrap import indent

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "sorting", "filtering", "site_pagination_traits"]:
    exec(import_cmd(components_dir, imp))

def site_detail(a_server_config, a_headers, a_site_id): 
    list_detail_url = "{0}/siteowner/v1/sites/{1}".format(a_server_config.to_url(), a_site_id)
    logging.debug("Querying Site Owner for details of site {} from {}".format(a_site_id, list_detail_url))

    response = session.get(list_detail_url, headers=a_headers)
    response.raise_for_status()
    
    site_list_json = response.json()
    return site_list_json

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Site Detail.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--owner_id", help="Organization ID")
    arg_parser.add_argument("--site_id", default="", help="Site Identifier")
    
    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    # << Server settings
    session = requests.Session()

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    logging.info("Running {0} for server={1} dc={2}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc))

    logging.info(json.dumps(site_detail(server, headers, args.site_id),indent=4))

if __name__ == "__main__":
    main()   