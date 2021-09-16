#!/usr/bin/python
import argparse
import logging
import requests
import base64
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "utils"))
from utils import *

session = requests.Session()

def get_token(a_client_id, a_client_secret, a_scope, a_server_config):
    basic_token = (a_client_id + ":" + a_client_secret).encode()

    headers = {
        "Authorization": "Basic " + base64.b64encode(basic_token).decode(),
    }
    params = {
        "grant_type": "client_credentials",
        "scope": a_scope,
    }
    response = session.post("{}/oauth/v1/token".format(a_server_config.to_url()), headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(response.text)
    return response.json()

def to_bearer_token_header(a_access_token, a_content_type=""):
    ret = {'Authorization': "Bearer {}".format(a_access_token)}
    if len(a_content_type) > 0:
        ret["Content-Type"] = a_content_type
    return ret

def token_from_jwt_or_oauth(a_jwt, a_client_id, a_client_secret, a_scope, a_server_config):
    token = a_jwt if len(a_jwt) > 0 else get_token(a_client_id=a_client_id, a_client_secret=a_client_secret, a_scope=a_scope, a_server_config=a_server_config)["access_token"]
    return token

def headers_from_jwt_or_oauth(a_jwt, a_client_id, a_client_secret, a_scope, a_server_config):
    return to_bearer_token_header(token_from_jwt_or_oauth(a_jwt, a_client_id, a_client_secret, a_scope, a_server_config))

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Exchange OAuth credentials for an API token")

    # script parameters:
    arg_parser.add_argument("--log-format", default='%(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
    arg_parser.add_argument("--log-level", default=logging.INFO)

    # server parameters:
    arg_parser.add_argument("--dc", default="us", required=True)
    arg_parser.add_argument("--env", default="", help="deploy environment (which determines server location)")
    arg_parser.add_argument("--oauth_id", default="", help="oauth_id")
    arg_parser.add_argument("--oauth_secret", default="", help="oauth_secret")
    arg_parser.add_argument("--oauth_scope", default="", help="oauth_scope")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc))
    
    token = get_token(a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    logging.info(token)


if __name__ == "__main__":
    main()    