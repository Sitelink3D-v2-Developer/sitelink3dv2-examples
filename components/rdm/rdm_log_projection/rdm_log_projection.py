#!/usr/bin/python
import os
import sys
import base64
import json

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_pagination_traits", "rdm_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

# For this example, we will simply count the instances of each RDM type that we find in the
# RDM log for our query so we have something to print to the user as evidence of success.
# This log processing however can implement any algorithm such as a deep copy (log replication)
# of the RDM log at one site to another site. See the site-copy tool in the tools repo at
# https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-api-tools/tree/main/sites/site-copy
# for just such an implementation of RDM log projection processing.
#
log_event_type_count_dict = {}

def ApplyLogEvent(a_event):
    
    decoded = json.loads(base64.b64decode(a_event["data_b64"]).decode('utf-8'))
    if decoded["_type"] not in log_event_type_count_dict:
        log_event_type_count_dict[decoded["_type"]] = 0

    log_event_type_count_dict[decoded["_type"]] = log_event_type_count_dict[decoded["_type"]] + 1



def query_rdm_by_domain_view(a_server_config, a_site_id, a_domain, a_view, a_headers, a_params={}):

    rdm_list_url = "{0}/rdm/v1/site/{1}/domain/{2}/view/{3}".format(a_server_config.to_url(), a_site_id, a_domain, a_view)
    response = session.get(rdm_list_url, headers=a_headers, params=a_params)
    response.raise_for_status()
    return response.json() # RDM view queries don't return 204s like the log projection event queries do so we can always return .json()

def query_rdm_log_by_domain_cursor(a_server_config, a_site_id, a_domain, a_headers, a_params={}):
    
    rdm_log_projection_url = "{0}/rdm_log/v1/site/{1}/domain/{2}/events".format(a_server_config.to_url(), a_site_id, a_domain)
    response = session.get(rdm_log_projection_url, headers=a_headers, params=a_params)
    response.raise_for_status()
    return None if response.status_code == 204 else response.json()

class RdmLogProjectionQuery():
    def __init__(self, a_server_config, a_site_id, a_domain, a_params, a_headers, a_result_callback=None):
        self.m_server_config = a_server_config
        self.m_site_id = a_site_id
        self.m_domain = a_domain
        self.m_params = a_params
        self.m_headers = a_headers
        self.m_result_callback = a_result_callback

    def query(self, a_params):
        params = self.m_params | a_params
        logging.debug("Using parameters:{}".format(json.dumps(params)))
        return query_rdm_log_by_domain_cursor(a_server_config=self.m_server_config, a_site_id=self.m_site_id, a_domain=self.m_domain, a_headers=self.m_headers, a_params=params)
    
    def result(self, a_value):
        if self.m_result_callback: 
            # Do some processing work that calling code is interested in.
            self.m_result_callback(a_value)
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
        logging.info("Querying RDM log for domain {}.".format(domain))
        page_traits = RdmLogProjectionPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
        log_projection_query = RdmLogProjectionQuery(a_server_config=server, a_site_id=args.site_id, a_domain=domain, a_params={"timeout_ms": 0}, a_headers=headers, a_result_callback=ApplyLogEvent)
        process_pages(a_page_traits=page_traits, a_page_query=log_projection_query)
    
    logging.info("RDM log projection found the following number of RDM types over all RDM domains:\n{}".format(json.dumps(log_event_type_count_dict, indent=4)))

if __name__ == "__main__":
    main()    
