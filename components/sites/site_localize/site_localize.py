#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["utils", "get_token", "rdm_traits", "args"]:
    exec(import_cmd(components_dir, imp))

def localize_site(a_server_config, a_site_id, a_file_id, a_file_rev, a_headers):

    localize_site_url = "{0}/transform/v1/sites/{1}/import".format(a_server_config.to_url(), a_site_id)

    payload_json = {
        "file_id"  : a_file_id,
        "file_rev" : a_file_rev
    }

    logging.info("post site localization file to transform service {}".format(localize_site_url))
    logging.debug(json.dumps(payload_json, indent=4))
    response = session.post(localize_site_url, headers=a_headers, data=json.dumps(payload_json))
    response_json = response.json()
    logging.debug("response from transform service {}".format(json.dumps(response_json, indent=4)))
    
def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_file_id, arg_file_rev] )
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    localize_site(a_server_config=server, a_site_id=args.site_id, a_file_id=args.file_id, a_file_rev=args.file_rev, a_headers=headers)

if __name__ == "__main__":
    main()    