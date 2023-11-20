#!/usr/bin/python
import os
import sys
from textwrap import indent

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args","get_token", "rdm_traits", "rdm_list", "rdm_pagination_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

# Return all objects in the specified RDM view that have a field of value specified. If None, return all objects
def query_rdm_object_properties_in_view(a_server_config, a_site_id, a_domain, a_view, a_headers, a_page_traits, a_callback, a_object_filter_field=None):
    
    more_data = True
    ret = []
    while more_data:
        rdm_list = query_rdm_by_domain_view(a_server_config=a_server_config, a_site_id=a_site_id, a_domain=a_domain, a_view=a_view, a_headers=a_headers, a_params=a_page_traits.params())
        more_data = a_page_traits.more_data(rdm_list)
        for fi in rdm_list["items"]:
            if a_callback(fi):
                ret.append(fi)
    return ret
    

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_rdm_view_name, arg_rdm_domain_default_sitelink, arg_pagination_page_limit, arg_pagination_start, arg_rdm_object_uuid])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    logging.info("Querying view {}".format(args.rdm_view))

    def callback(a_item):
        if a_item["id"] == args.rdm_object_uuid or len(args.rdm_object_uuid) == 0:
                logging.info(json.dumps(a_item,indent=4))

    query_rdm_object_properties_in_view(a_server_config=server, a_site_id=args.site_id, a_domain=args.rdm_domain, a_view=args.rdm_view, a_headers=headers, a_page_traits=RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start), a_callback=callback)

if __name__ == "__main__":
    main()    
