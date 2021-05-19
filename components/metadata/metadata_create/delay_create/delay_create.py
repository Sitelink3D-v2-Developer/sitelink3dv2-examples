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

session = requests.Session()

def create_delay(a_site_id, a_server_config, a_delay_name, a_delay_code, a_headers):
    
    delay_rdm_bean = DelayMetadataTraits.post_bean_json(a_delay_name=a_delay_name, a_id=str(uuid.uuid4()), a_delay_code=a_delay_code)

    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(), a_site_id)
    logging.debug ("Upload RDM to {}".format(url))
    
    json.dumps(delay_rdm_bean,indent=4)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(delay_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("Delay RDM payload: {}".format(json.dumps(delay_rdm_bean, indent=4)))

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    logging.debug ("create delay returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))


def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Upload a delay.")

    # script parameters:
    arg_parser.add_argument("--log-format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    arg_parser.add_argument("--log-level", default=logging.INFO)

    # server parameters:
    arg_parser.add_argument("--dc", default="", required=True)
    arg_parser.add_argument("--env", default="", help="deploy environment (which determines server location)")
    arg_parser.add_argument("--oauth_id", default="", help="oauth_id")
    arg_parser.add_argument("--oauth_secret", default="", help="oauth_secret")
    arg_parser.add_argument("--oauth_scope", default="", help="oauth_scope")

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--delay_name", default="", help="The name of the delay", required=True)
    arg_parser.add_argument("--delay_code", default=None, help="An optional code to describe the delay")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
   
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    token = get_token(a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    create_delay(a_site_id=args.site_id, a_server_config=server, a_delay_name=args.delay_name, a_delay_code=args.delay_code, a_headers=to_bearer_token_content_header(token["access_token"]))

if __name__ == "__main__":
    main()    

