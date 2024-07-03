#!/usr/bin/python

# This example demonstrates the ability to download design data surveyed on machine control clients as a single merged file via the Design File service. 
# Device Design Data is stored within Sitelink3D once it is pushed to the cloud and is accessed from the cloud using an RDM query with the view 
# "v_sl_deviceDesignObject_by_deviceURN". An RDM view is a named definition of the type of metadata being requested and how that data is keyed in the response.

import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "get_token", "file_download"]:
    exec(import_cmd(components_dir, imp))
 
session = requests.Session()

def get_merge_job(a_server_config, a_site_id, a_job_id, a_headers, a_long_poll=True):
    url = "{0}/designfile/v1/sites/{1}/merge_jobs/{2}".format(a_server_config.to_url(), a_site_id, a_job_id)
    params = {}
    if a_long_poll:
        params["long_poll"] = "true"
    return session.get(url, params=params, headers=a_headers)

def merge_design_objects(a_server_config, a_site_id, a_particular, a_design_object_ids, a_headers):
    url = "{0}/designfile/v1/sites/{1}/merge_jobs".format(a_server_config.to_url(), a_site_id)
    body = {
        "particular": a_particular,
        "design_object_ids": a_design_object_ids
    }
    response =  session.post(url, headers=a_headers, data=json.dumps(body))
    response_body = response.json()
    logging.info(json.dumps(response_body, indent=4))
    job_id = response_body["id"]
    while True:
        response = get_merge_job(a_server_config, a_site_id, job_id, a_headers)
        if response.status_code == 504:
            continue
        break
    return response.json()

def main():

    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id,
                                        a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
    device_design_object_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink",
                                                              a_view="v_sl_deviceDesignObject_by_deviceURN", a_headers=headers, a_params=page_traits.params())["items"]

    logging.info("Found {} device design objects".format(len(device_design_object_list)))
    output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
    
    # we look to cache all the device designs in a list which we will then use to request a merge.
    design_file_uuids = []

    for fi in device_design_object_list:
        design_file_uuids.append(fi["value"]["doFileUUID"])

    logging.debug(json.dumps(design_file_uuids,indent=4))

    particulars = ["MAXML", "DXF"]
    for target_particular in particulars:
        response = merge_design_objects(a_server_config=server, a_site_id=args.site_id, a_particular=target_particular, a_design_object_ids=design_file_uuids, a_headers=headers)
        logging.debug(json.dumps(response, indent=4))
        download_file(server, args.site_id, response["file_id"], a_headers=headers, a_target_dir=output_dir, a_target_name="{}.{}".format(response["file_id"],target_particular.lower()))

if __name__ == "__main__":
    main()
