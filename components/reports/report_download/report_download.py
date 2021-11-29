#!/usr/bin/python
import argparse
import json
import logging
import os
import sys
import requests
import itertools

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "reports"))

from get_token import *
from utils import *
from args import *
from report_pagination_traits import *

session = requests.Session()

def headers_from_report_url(a_report_url, a_headers):
    if "amazonaws.com" in a_report_url:
        return {}
    else:
        return a_headers

def fetch_report_paginated(a_report_url, a_headers, a_params):
    response = session.get(a_report_url, headers=headers_from_report_url(a_report_url, a_headers), allow_redirects=False, params=a_params)
    if response.status_code in [301,302]:
        response = requests.get(response.headers['Location'], params=a_params)
    response.raise_for_status()

    return response.json()

def download_report_binary(a_report_url, a_headers, a_target_dir, a_report_name):
    response = session.get(a_report_url, headers=headers_from_report_url(a_report_url, a_headers), allow_redirects=False)
    if response.status_code in [301,302]:
        response = requests.get(response.headers['Location'])
    response.raise_for_status()

    output_file = os.path.join(a_target_dir, a_report_name)
    with open(output_file, "wb") as f:
        f.write(response.content)
        logging.info("Saved report {}".format(output_file))    

def download_report(a_report_url, a_headers, a_target_dir, a_report_name):
    
    paginate_report = a_report_url.startswith("https") and a_report_url.endswith("hauls") # reports of this format are the only ones to paginate
    if not os.path.exists(a_target_dir):
        os.makedirs(a_target_dir, exist_ok=True)

    if paginate_report:
        logging.info("Downloading paginated report.")
        page_traits = ReportDataPaginationTraits(a_page_size="500", a_start="0")
        more_data = True

        output_list = []
        while True:
            report_list = fetch_report_paginated(a_report_url=a_report_url, a_headers=a_headers, a_params=page_traits.params())       
            more_data = page_traits.more_data(report_list)
            logging.info ("Found {} items {}".format(len(report_list["data"]), "({})".format("unpaginated" if page_traits.page_number() == 1 else "last page") if not more_data else "(page {})".format(page_traits.page_number())))

            output_list.append(report_list["data"])

            if not more_data:
                break
        output_file = os.path.join(a_target_dir, a_report_name)
        with open(output_file, "w") as f:
            f.write(json.dumps(list(itertools.chain.from_iterable(output_list)), indent=4))
            logging.info("Saved report {}".format(output_file))  

    else:
        logging.info("Downloading binary report.")
        download_report_binary(a_report_url, a_headers, a_target_dir, a_report_name)


def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description=os.path.basename(os.path.realpath(__file__)))

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    arg_parser = add_arguments_pagination(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--report_url", required=True)
    arg_parser.add_argument("--report_name", required=True)


    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(current_dir, args.site_id[0:12])
    
    download_report(a_report_url=args.report_url, a_headers=headers, a_target_dir=output_dir, a_report_name=args.report_name)       
    

if __name__ == "__main__":
    main()    
