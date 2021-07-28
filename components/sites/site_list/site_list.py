#!/usr/bin/python
import argparse
import json
import logging
import os
import requests
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "metadata"))

from get_token import *
from utils import *
from metadata_traits import *
from args import *

def list_sites(a_server_config, a_owner_id, a_headers):

    list_site_url = "{0}/siteowner/v1/owners/{1}/sites".format(a_server_config.to_url(), a_owner_id)

    print(list_site_url)
    response = session.get(list_site_url, headers=a_headers)#, params={ "fetch_size":100, "order":"rdm_name", "filter":"e30", "archived":False })
    response.raise_for_status()
    
    site_list_json = response.json()
    return site_list_json

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Site List.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser.add_argument("--jwt", default="", help="jwt")

    # request parameters:
    arg_parser.add_argument("--owner_id", help="Organization ID", required=True)
    
    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments


    # << Server settings
    session = requests.Session()

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    headers = to_bearer_token_header(a_access_token=args.jwt)

    logging.info("Running {0} for server={1} dc={2} owner={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.owner_id))

    sites = list_sites(a_server_config=server, a_owner_id=args.owner_id, a_headers=headers)

    logging.info("Found {} sites.".format(len(sites["items"])))

    for site in sites["items"]:
        try:
            logging.info("'{}' at lat:{}, lon:{} in timezone {}".format(site["name"], site["rdm_marker"]["lat"], site["rdm_marker"]["lon"], site["rdm_timezone"])) 
        except KeyError as err:  
            pass  
        

if __name__ == "__main__":
    main()   