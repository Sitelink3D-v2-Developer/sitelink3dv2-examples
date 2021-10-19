#!/usr/bin/python
import argparse
import json
import logging
import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "metadata", "metadata_list"))

from get_token import *
from utils import *
from args import *
from metadata_list import *

session = requests.Session()


def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Report Listing")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--start", default="", help="Start from here")
    arg_parser.add_argument("--page_limit", default="500", help="Page size")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    report_list_url = "{0}/reporting/v1/{1}/longterms/?order=issued_at&filter=e30".format(server.to_url(), args.site_id)

    response = session.get(report_list_url, headers=headers)
    response.raise_for_status()
   
    report_list = response.json()

    logging.info(json.dumps(report_list, indent=4))


if __name__ == "__main__":
    main()    
