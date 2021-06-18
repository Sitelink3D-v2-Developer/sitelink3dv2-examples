#!/usr/bin/python
import argparse
import json
import logging
import os
import sys
import requests
import base64

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))

from get_token import *
from utils import *
from args import *


session = requests.Session()

def smartview_app_list(a_server_config):

    sv_app_list_url = "{0}/smart_view/unstable/smartapps".format(a_server_config.to_url())

    response = session.get(sv_app_list_url)
    response.raise_for_status()
    app_list = response.json()
   
    return app_list

def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Smartview App Listing")
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc))

    app_list = smartview_app_list(a_server_config=server)

    logging.info ("Found {} apps".format(len(app_list)))
    for app in app_list:
        print("SmartView Application '{}' at version {}: {}".format(app["name"], app["version"], app["description"]))
        logging.debug (json.dumps(app, sort_keys=True, indent=4))

if __name__ == "__main__":
    main()    
