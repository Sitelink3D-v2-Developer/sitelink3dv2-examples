#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()


def main():
    script_name = os.path.basename(os.path.realpath(__file__))
    
    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_operation])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center="us")
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), "us", args.site_id))
    # << Server & logging configuration

    # >> Authorization
    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    # << Authorization

    # First get the details of the site with the specified identifier so we can access the uuid that siteowner will require
    site_details = site_detail(server, headers, args.site_id)
    logging.debug("Site details: {}".format(json.dumps(site_details, indent=4)))

    url = "{}/siteowner/v1/sites/{}/{}".format(server.to_url(), site_details["uuid"], args.operation)
    headers["etag"] = site_details["etag"]

    logging.info("{} site {} with {}".format(args.operation, args.site_id, url))
    response = session.put(url, headers=headers)
    
    owner_details = response.json()
    logging.info("response from site owner {}:{}".format(response.status_code, json.dumps(owner_details, indent=4)))


if __name__ == "__main__":
    main()    
