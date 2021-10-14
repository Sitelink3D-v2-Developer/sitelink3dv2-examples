#!/usr/bin/python
import argparse
import logging
import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..","..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..","..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "metadata_list"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", ".."))

from get_token import *
from utils import *
from metadata_traits import *
from args import *
from metadata_list import *

session = requests.Session()

def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Paginating RDM data")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.DEBUG)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--start", default="", help="Start from here")
    arg_parser.add_argument("--page_limit", default="", help="Page size")
    arg_parser.add_argument("--rdm_view", default="v_sl_task_by_name", help="The view to query RDM by")
    arg_parser.add_argument("--rdm_domain", default="sitelink", help="The domain that the view exists in")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    logging.info("Querying view {}".format(args.rdm_view))
    start_key=args.start
    pagination_frame = None
    page_number = 1
    while True:
        metadata_list = query_metadata_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain=args.rdm_domain, a_view=args.rdm_view, a_page_limit=args.page_limit, a_start=start_key, a_end="", a_headers=headers)
        pagination_frame = metadata_list["last_excl"]
        
        logging.info ("Found {} items {}".format(len(metadata_list["items"]), "({})".format("unpaginated" if page_number == 1 else "last page") if not pagination_frame else "(page {})".format(page_number)))

        for fi in metadata_list["items"]:
            obj = Metadata.traits_factory(fi["value"])
            if obj is not None:
                logging.info("Found {} {}".format(obj.class_name(), obj.object_details()))        

        if pagination_frame is None:
            break
        else:
            start_key=pagination_frame["key"]
            page_number += 1

    
           


if __name__ == "__main__":
    main()    
