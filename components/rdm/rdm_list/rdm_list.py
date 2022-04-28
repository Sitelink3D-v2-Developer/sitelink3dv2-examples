#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def query_rdm_by_domain_view(a_server_config, a_site_id, a_domain, a_view, a_headers, a_params={}):

    rdm_list_url = "{0}/rdm/v1/site/{1}/domain/{2}/view/{3}".format(a_server_config.to_url(), a_site_id, a_domain, a_view)
    response = session.get(rdm_list_url, headers=a_headers, params=a_params)
    response.raise_for_status()
    return response.json() 

class RdmListPageQuery():
    def __init__(self, a_server_config, a_site_id, a_domain, a_view, a_params, a_headers, a_result_callback=None):
        self.m_server_config = a_server_config
        self.m_site_id = a_site_id
        self.m_domain = a_domain
        self.m_view = a_view
        self.m_params = a_params
        self.m_headers = a_headers
        self.m_result_callback = a_result_callback

    def query(self, a_params):
        params = self.m_params | a_params
        logging.debug("Using parameters:{}".format(json.dumps(params)))
        return query_rdm_by_domain_view(a_server_config=self.m_server_config, a_site_id=self.m_site_id, a_domain=self.m_domain, a_view=self.m_view, a_headers=self.m_headers, a_params=params)
    
    def result(self, a_value):
        if self.m_result_callback: 
            # Do some processing work that calling code is interested in.
            self.m_result_callback(a_value["value"])
        else: 
            # Some default result processing in case a callback wasn't specified.
            obj = Rdm.traits_factory(a_value["value"])
            if obj is not None:
                logging.info("Found {} {}".format(obj.class_name(), obj.object_details()))

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    rdm_domains = ["sitelink", "file_system", "operator", "reporting"]

    for domain in rdm_domains:
        logging.info("Querying RDM {} domain for views.".format(domain))

        rdm_view_list_url = "{0}/rdm/v1/site/{1}/domain/{2}/view/_view".format(server.to_url(), args.site_id, domain)

        response = session.get(rdm_view_list_url, headers=headers, params={"limit":args.page_limit})
        rdm_view_list = response.json()
        logging.debug (json.dumps(rdm_view_list, sort_keys=True, indent=4))
        view_list_length = 0
        try:
            view_list_length = len(rdm_view_list["items"])
        except KeyError:
            logging.info("No views in this RDM domain.")
            continue
        logging.info("Found {} views.".format(view_list_length))
        for rdm_view in rdm_view_list["items"]:
            
            for state in [{"archived":False},{"archived":True}]:
                logging.info("querying view {} ({})".format(rdm_view["id"], state))
                page_traits = RdmPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
                file_list_query = RdmListPageQuery(a_server_config=server, a_site_id=args.site_id, a_domain=domain, a_view=rdm_view["id"], a_params=state, a_headers=headers)
                process_pages(a_page_traits=page_traits, a_page_query=file_list_query)

if __name__ == "__main__":
    main()    
