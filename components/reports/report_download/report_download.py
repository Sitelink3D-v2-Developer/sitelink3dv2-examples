#!/usr/bin/python
import os
import sys
import itertools

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["utils", "site_detail", "get_token", "report_pagination_traits", "args"]:
    exec(import_cmd(components_dir, imp))

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

def download_report(a_report_url, a_headers, a_target_dir, a_report_name, a_page_size="500"):
    logging.debug(a_report_url)
    if not os.path.exists(a_target_dir):
        os.makedirs(a_target_dir, exist_ok=True)

    logging.info("Downloading binary report.")
    download_report_binary(a_report_url, a_headers, a_target_dir, a_report_name)


def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_report_name, arg_report_url, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
    download_report(a_report_url=args.report_url, a_headers=headers, a_target_dir=output_dir, a_report_name=args.report_name, a_page_size=args.page_limit)       

if __name__ == "__main__":
    main()    
