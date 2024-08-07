#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def query_nested_files_and_folders(a_server_config, a_site_id, a_parent_folder_uuid, a_headers):

    files_and_folders = []
    page_traits = RdmViewPaginationTraits(a_page_size="500", a_start=[a_parent_folder_uuid], a_end=[a_parent_folder_uuid, None])
    rj = query_rdm_by_domain_view(a_server_config=a_server_config, a_site_id=a_site_id, a_domain="file_system", a_view="v_fs_files_by_folder", a_headers=a_headers, a_params=page_traits.params())

    for fi in rj["items"]:
        files_and_folders.append(fi)
        if fi["value"]["_type"] == "fs::folder":
            files_and_folders = files_and_folders + query_nested_files_and_folders(a_server_config=a_server_config, a_site_id=a_site_id, a_parent_folder_uuid=fi["id"], a_headers=a_headers)

    return files_and_folders


def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    
    for state in [{"archived":False},{"archived":True}]:
        
        page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)

        logging.info("Listing file_system domain entries")
        file_list_query = RdmListPageQuery(a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_view="v_fs_files_by_folder", a_params=state, a_headers=headers)
        process_pages(a_page_traits=page_traits, a_page_query=file_list_query)

if __name__ == "__main__":
    main()    
