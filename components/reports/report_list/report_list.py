#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["utils", "get_token", "filtering", "sorting", "args", "report_pagination_traits", "metadata_list"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

class ReportListPageQuery():
    def __init__(self, a_server_config, a_site_id, a_params, a_headers):
        self.m_server_config = a_server_config
        self.m_site_id = a_site_id
        self.m_params = a_params
        self.m_headers = a_headers

    def query(self, a_params):
        params = self.m_params | a_params
        logging.debug("Using parameters:{}".format(json.dumps(params)))
        report_list_url = "{0}/reporting/v1/{1}/longterms/".format(self.m_server_config.to_url(), self.m_site_id)
        response = session.get(report_list_url, headers=self.m_headers, params=params)
        response.raise_for_status()     
        return response.json()

    @staticmethod
    def result(a_value):
        try:
            logging.info("'{}' of type:{} run by {} ({})".format(a_value["params"]["name"], a_value["job_type"], a_value["issued_by"], "archived" if a_value["archived"] else "active")) 
        except KeyError as err:  
            pass 

def main():
    # >> Arguments

    arg_parser = argparse.ArgumentParser(description="Report Listing")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)
    arg_parser = add_arguments_sorting(arg_parser)
    arg_parser = add_arguments_pagination(arg_parser)
    arg_parser = add_arguments_filtering(arg_parser, ["issued_since_epoch","job_type","name","issued_by","status"])

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)


    sort_traits = SortTraits(a_sort_field=args.sort_field, a_sort_order=args.sort_order)
    filters = add_filter_term(a_filter={}, a_field_name="job_type", a_operation="in", a_value=[args.filter_job_type])
    if len(args.filter_issued_since_epoch) > 0:    
        filters = add_filter_term(a_filter=filters, a_field_name="issued_at", a_operation=">", a_value=int(args.filter_issued_since_epoch))
    filters = add_filter_term(a_filter=filters, a_field_name="params.name", a_operation="=", a_value=args.filter_name)
    filters = add_filter_term(a_filter=filters, a_field_name="issued_by", a_operation="in", a_value=[args.filter_issued_by])
    filters = add_filter_term(a_filter=filters, a_field_name="status", a_operation="in", a_value=[args.filter_status])

    for state in [{"archived":False},{"archived":True}]:
        
        page_traits = ReportListPaginationTraits(a_page_size=args.page_limit, a_start=args.start)

        report_list_query = ReportListPageQuery(a_server_config=server, a_site_id=args.site_id, a_params=sort_traits.params(filter_params(state, filters)), a_headers=headers)
        process_pages(a_page_traits=page_traits, a_page_query=report_list_query)


if __name__ == "__main__":
    main()    
