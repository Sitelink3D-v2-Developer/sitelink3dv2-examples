#!/usr/bin/python
import os
import sys
from rdm_archive_restore import *

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()


def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Archive and Restore RDM Objects")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)
    arg_parser = add_arguments_pagination(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--rdm_view", help="The view to query RDM by", required=True)
    arg_parser.add_argument("--rdm_domain", default="sitelink", help="The domain that the view exists in")
    arg_parser.add_argument("--operation", default="archive", help="can be archive or restore")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    
    page_traits = RdmPaginationTraits(a_page_size=args.page_limit, a_start=args.start)

    logging.info("{} objects in RDM view {}".format("Archiving" if args.operation == "archive" else "Restoring", args.rdm_view))

    # Take an existing RDM object and write it back to RDM with the archived flag set to archive it.
    def archive_object(a_obj):
        if args.operation == "archive":
            archive_rdm_object(a_rdm_object_bean=a_obj, a_domain=args.rdm_domain, a_server_config=server, a_site_id=args.site_id, a_headers=headers)
        else:
            restore_rdm_object(a_rdm_object_bean=a_obj, a_domain=args.rdm_domain, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

    rdm_view_list_query = RdmListPageQuery(a_server_config=server, a_site_id=args.site_id, a_domain=args.rdm_domain, a_view=args.rdm_view, a_params={"archived":(args.operation != "archive")}, a_headers=headers, a_result_callback=archive_object)
    process_pages(a_page_traits=page_traits, a_page_query=rdm_view_list_query)


if __name__ == "__main__":
    main()    
