#!/usr/bin/python
import argparse
import json
import logging
import os
import requests
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))

from get_token import *
from args import *

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Organization Get.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--owner_id", help="Organization ID", required=True)
    
    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments


    # << Server settings
    session = requests.Session()

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    logging.info("Running {0} for server={1} dc={2} owner={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.owner_id))

    owner_get_url = "{0}/siteowner/v1/owners/{1}".format(server.to_url(), args.owner_id)

    logging.info("Get owner details from site owner {}".format(owner_get_url))
    response = session.get(owner_get_url, headers=headers)
    
    owner_details = response.json()
    logging.info("response from site owner {}".format(json.dumps(owner_details, indent=4)))

if __name__ == "__main__":
    main()   