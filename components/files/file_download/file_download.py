#!/usr/bin/python
import argparse
import logging
import os
import sys
import requests
import json
import base64
import uuid
import time
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))

from get_token import *
from utils import *
from args import *

session = requests.Session()

def download_file(a_server_config, a_site_id, a_file_uuid, a_headers):

    get_file_url = "{0}/file/v1/sites/{1}/files/{2}/url".format(a_server_config.to_url(), a_site_id, a_file_uuid)

    # get the url of the file
    response = session.get(get_file_url, headers=a_headers)
    response.raise_for_status()

    # get the content of the url
    url = "{0}{1}".format(a_server_config.to_url(), response.text)
    print ("get file {0} by url {1}".format(a_file_uuid, url))
    response = session.get(url, headers=a_headers, stream=True)
    response.raise_for_status()

    current_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(current_dir, a_site_id)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_file = os.path.join(output_dir, a_file_uuid)
    with open(output_file, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)



def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Upload a file.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    arg_parser.add_argument("--file_uuid", default=str(uuid.uuid4()), help="UUID of file")

    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
   
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    download_file(a_server_config=server, a_site_id=args.site_id, a_file_uuid=args.file_uuid, a_headers=headers)

if __name__ == "__main__":
    main()    

