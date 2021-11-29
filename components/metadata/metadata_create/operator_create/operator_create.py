#!/usr/bin/python
import argparse
import logging
import os
import sys
import requests
import json
import base64
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "metadata"))

from get_token import *
from utils import *
from metadata_traits import *
from args import *

session = requests.Session()

def create_operator(a_site_id, a_server_config, a_first_name, a_last_name, a_code, a_headers):

    operator_rdm_bean = OperatorMetadataTraits.post_bean_json(a_first_name=a_first_name, a_last_name=a_last_name, a_code=a_code)

    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(), a_site_id)
    logging.debug ("Upload RDM to {}".format(url))
    
    json.dumps(operator_rdm_bean,indent=4)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(operator_rdm_bean).encode('utf-8')).decode('utf-8') }
    print("Operator RDM payload: {}".format(json.dumps(operator_rdm_bean, indent=4)))

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    if response.status_code == 200:
        logging.info("Operator created.")
    logging.debug ("create operator returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))


def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Upload an Operator.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--operator_first_name", default="", help="The first name of the operator", required=True)
    arg_parser.add_argument("--operator_last_name", default=None, help="The last name of the operator", required=True)
    arg_parser.add_argument("--operator_code", default=None, help="An optional code to describe the operator")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
   
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    
    create_operator(a_site_id=args.site_id, a_server_config=server, a_first_name=args.operator_first_name, a_last_name=args.operator_last_name, a_code=args.operator_code, a_headers=headers)


if __name__ == "__main__":
    main()    
