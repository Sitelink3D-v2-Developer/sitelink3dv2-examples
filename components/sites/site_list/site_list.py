#!/usr/bin/python
import argparse
import json
import logging
import os
import requests
import sys
import itertools

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils", "parameters"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "metadata"))

from get_token import *
from utils import *
from sorting import *
from metadata_traits import *
from args import *
from filtering import *
from site_pagination_traits import *

def list_sites(a_server_config, a_owner_id, a_headers, a_params):

    list_site_url = "{0}/siteowner/v1/owners/{1}/sites".format(a_server_config.to_url(), a_owner_id)

    logging.info("get site list from site owner {}".format(list_site_url))
    response = session.get(list_site_url, headers=a_headers, params=a_params)
    response.raise_for_status()
    
    site_list_json = response.json()
    logging.debug("response from site owner {}".format(json.dumps(site_list_json, indent=4)))
    return site_list_json

class SiteListPageQuery():
    def __init__(self, a_server_config, a_owner_id, a_params, a_headers):
        self.m_server_config = a_server_config
        self.m_owner_id = a_owner_id
        self.m_params = a_params
        self.m_headers = a_headers

    def query(self, a_params):
        params = self.m_params | a_params
        logging.debug("Using parameters:{}".format(json.dumps(params)))
        return list_sites(a_server_config=self.m_server_config, a_owner_id=self.m_owner_id, a_headers=self.m_headers, a_params=params)
    
    @staticmethod
    def result(a_value):
        try:
            logging.info("'{}' at lat:{}, lon:{} in timezone {} ({})".format(a_value["rdm_name"], a_value["rdm_marker"]["lat"], a_value["rdm_marker"]["lon"], a_value["rdm_timezone"], "archived" if a_value["archived"] else "active")) 
        except KeyError as err:  
            pass 

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Site List.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)
    arg_parser = add_arguments_sorting(arg_parser)
    arg_parser = add_arguments_pagination(arg_parser)
    arg_parser = add_arguments_filtering(arg_parser, ["name_includes","owner_email_includes","created_since_epoch","cell_size_equals","data_center_equals"])

    # request parameters:
    arg_parser.add_argument("--owner_id", help="Organization ID", required=True)
    
    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments


    # << Server settings
    session = requests.Session()

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    logging.info("Running {0} for server={1} dc={2} owner={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.owner_id))

    sort_traits = SortTraits(a_sort_field=args.sort_field, a_sort_order=args.sort_order)
    
    filters = add_filter_term(a_filter={}, a_field_name="rdm_name", a_operation="=", a_value=args.filter_name_includes)
    filters = add_filter_term(a_filter=filters, a_field_name="owner_email", a_operation="=", a_value=args.filter_owner_email_includes)
    if len(args.filter_created_since_epoch) > 0:
        filters = add_filter_term(a_filter=filters, a_field_name="create_timestamp_ms", a_operation=">", a_value=int(args.filter_created_since_epoch))
    filters = add_filter_term(a_filter=filters, a_field_name="region", a_operation="in", a_value=[args.filter_cell_size_equals])
    filters = add_filter_term(a_filter=filters, a_field_name="dc", a_operation="in", a_value=[args.filter_data_center_equals])

    for state in [{"archived":False},{"archived":True}]:
        
        page_traits = SitePaginationTraits(a_page_size=args.page_limit, a_start=args.start)

        site_list_query = SiteListPageQuery(a_server_config=server, a_owner_id=args.owner_id, a_params=sort_traits.params(filter_params(state, filters)), a_headers=headers)
        process_pages(a_page_traits=page_traits, a_page_query=site_list_query)

if __name__ == "__main__":
    main()   