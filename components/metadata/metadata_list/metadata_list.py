#!/usr/bin/python
import argparse
import json
import logging
import os
import sys
import requests
import base64
import json

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

from get_token import *
from utils import *
from metadata_traits import *
from args import *

session = requests.Session()

def query_metadata_by_domain_view(a_server_config, a_site_id, a_domain, a_view, a_page_limit, a_start, a_end, a_headers):

    rdm_list_url = "{0}/rdm/v1/site/{1}/domain/{2}/view/{3}".format(a_server_config.to_url(), a_site_id, a_domain, a_view)

    # Listing entries
    params = {}
    if len(a_page_limit) > 0:
        params["limit"] = a_page_limit
    if len(a_start) > 0:
        logging.debug("start key sepcified: {}".format(a_start))
        params["start"] = base64.urlsafe_b64encode(json.dumps(a_start).encode('utf-8')).decode('utf-8').rstrip("=")
    if len(a_end) > 0:
        logging.debug("end key sepcified: {}".format(a_end))
        params["end"] = base64.urlsafe_b64encode(json.dumps(a_end).encode('utf-8')).decode('utf-8').rstrip("=")
    
    response = session.get(rdm_list_url, headers=a_headers, params=params)
    response.raise_for_status()
   
    return response.json() 

def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Metadata Listing")

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

    rdm_domains = ["sitelink", "file_system", "operator", "reporting"]

    for domain in rdm_domains:
        logging.info("Querying RDM {} domain for views.".format(domain))

        rdm_view_list_url = "{0}/rdm/v1/site/{1}/domain/{2}/view/_view".format(server.to_url(), args.site_id, domain)

        response = session.get(rdm_view_list_url, headers=headers, params={"limit":args.page_limit})
        rdm_view_list = response.json()
        logging.debug (json.dumps(rdm_view_list, sort_keys=True, indent=4))
        view_list_length = 0
        try:
            view_list_length = len(rdm_view_list["items"])
        except KeyError:
            logging.info("No views in this RDM domain.")
            continue
        logging.info("Found {} views.".format(view_list_length))
        for rdm_view in rdm_view_list["items"]:
            logging.info("querying view {}".format(rdm_view["id"]))
            metadata_list = query_metadata_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain=domain, a_view=rdm_view["id"], a_page_limit=args.page_limit, a_start=args.start, a_end="", a_headers=headers)["items"]

            logging.info ("Found {} items".format(len(metadata_list)))
            for fi in metadata_list:
                logging.debug (json.dumps(fi, sort_keys=True, indent=4))
                obj = Metadata.traits_factory(fi["value"])
                if obj is not None:
                    logging.info("Found {} {}".format(obj.class_name(), obj.object_details()))
           


if __name__ == "__main__":
    main()    
