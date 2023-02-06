#!/usr/bin/python

import logging
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "sorting", "filtering", "site_pagination_traits"]:
    exec(import_cmd(components_dir, imp))

def list_sites(a_server_config, a_headers, a_params, a_owner_id=None):

    list_site_url = "{0}/siteowner/v1/sites".format(a_server_config.to_url())
    if a_owner_id is not None and len(a_owner_id) > 0:
        logging.debug("Querying Site Owner using Owner ID {}".format(a_owner_id))
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
        return list_sites(a_server_config=self.m_server_config, a_headers=self.m_headers, a_params=params, a_owner_id=self.m_owner_id)
    
    @staticmethod
    def result(a_value):
        try:
            logging.info("'{}' at lat:{}, lon:{} in timezone {} ({})".format(a_value["rdm_name"], a_value["rdm_marker"]["lat"], a_value["rdm_marker"]["lon"], a_value["rdm_timezone"], "archived" if a_value["archived"] else "active")) 
        except KeyError as err:  
            pass 

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_owner_uuid, arg_sort_field, arg_sort_order, arg_pagination_page_limit, arg_pagination_start], a_arg_filter_list=["name_includes","owner_email_includes","created_since_epoch","cell_size_equals","data_center_equals"] )
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} owner={3}".format(script_name, server.to_url(), args.dc, args.site_owner_uuid))
    # << Server & logging configuration

    # >> Authorization
    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    # << Authorization

    sort_traits = SortTraits(a_sort_field=args.sort_field, a_sort_order=args.sort_order)
    
    filters = add_filter_term(a_filter={}, a_field_name="rdm_name", a_operation="=", a_value=args.filter_name_includes)
    filters = add_filter_term(a_filter=filters, a_field_name="owner_email", a_operation="=", a_value=args.filter_owner_email_includes)
    if len(args.filter_created_since_epoch) > 0:
        filters = add_filter_term(a_filter=filters, a_field_name="create_timestamp_ms", a_operation=">", a_value=int(args.filter_created_since_epoch))
    filters = add_filter_term(a_filter=filters, a_field_name="region", a_operation="in", a_value=[args.filter_cell_size_equals])
    filters = add_filter_term(a_filter=filters, a_field_name="dc", a_operation="in", a_value=[args.filter_data_center_equals])

    for state in [{"archived":False},{"archived":True}]:
        
        page_traits = SitePaginationTraits(a_page_size=args.page_limit, a_start=args.start)

        site_list_query = SiteListPageQuery(a_server_config=server, a_params=sort_traits.params(filter_params(state, filters)), a_headers=headers, a_owner_id=args.site_owner_uuid)
        process_pages(a_page_traits=page_traits, a_page_query=site_list_query)

if __name__ == "__main__":
    main()   