#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args","get_token", "rdm_traits", "rdm_list", "rdm_pagination_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Paginating RDM data")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    arg_parser = add_arguments_pagination(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
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

    page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
    more_data = True
    while more_data:
        rdm_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain=args.rdm_domain, a_view=args.rdm_view, a_headers=headers, a_params=page_traits.params())
        more_data = page_traits.more_data(rdm_list)

        num_items = len(rdm_list["items"])
        if more_data:
            logging.info("Found {} items (page {})".format(num_items, page_traits.page_number()))
        elif page_traits.page_number() == 1:
            logging.info("Found {} items (unpaginated)".format(num_items))
        else:
            logging.info("Found {} items (last page)".format(num_items))

        for fi in rdm_list["items"]:
            obj = Rdm.traits_factory(fi["value"])
            if obj is not None:
                logging.info("Found {} {}".format(obj.class_name(), obj.object_details()))        

if __name__ == "__main__":
    main()    
