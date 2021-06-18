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

def query_files(a_server_config, a_site_id, a_page_limit, a_start, a_headers):

    rdm_list_files_url = "{0}/rdm/v1/site/{1}/domain/file_system/view/v_fs_files_by_folder".format(a_server_config.to_url(), a_site_id)

    # Listing files
    params = {}
    if len(a_page_limit) > 0:
        params["limit"] = a_page_limit
    if len(a_start) > 0:
        s_id = json.dumps([a_start]).encode()
        params["start"] = base64.urlsafe_b64encode(s_id).replace("=", "", 4)

    response = session.get(rdm_list_files_url, headers=a_headers, params=params)
    response.raise_for_status()
    file_list = response.json()["items"]

    logging.debug("Files listing result for site {0} \n{1}".format(a_site_id, json.dumps(file_list, indent=4)))
    
    return file_list

def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Files Listing")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--start", default="", help="Start from here")
    arg_parser.add_argument("--page_limit", default="10", help="Page size")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    file_list = query_files(a_server_config=server, a_site_id=args.site_id, a_page_limit=args.page_limit, a_start=args.start, a_headers=headers)

    logging.info ("Found {} files".format(len(file_list)))
    for fi in file_list:
        logging.info (json.dumps(fi, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()    
