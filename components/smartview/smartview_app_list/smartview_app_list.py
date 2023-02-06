#!/usr/bin/python
import json
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def smartview_app_list(a_server_config):

    sv_app_list_url = "{0}/smart_view/unstable/smartapps".format(a_server_config.to_url())

    response = session.get(sv_app_list_url)
    response.raise_for_status()
    app_list = response.json()
   
    return app_list

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2}".format(script_name, server.to_url(), args.dc))
    # << Server & logging configuration

    app_list = smartview_app_list(a_server_config=server)

    logging.info ("Found {} apps".format(len(app_list)))
    for app in app_list:
        print("SmartView Application '{}' at version {}: {}".format(app["name"], app["version"], app["description"]))
        logging.debug (json.dumps(app, sort_keys=True, indent=4))

if __name__ == "__main__":
    main()    
