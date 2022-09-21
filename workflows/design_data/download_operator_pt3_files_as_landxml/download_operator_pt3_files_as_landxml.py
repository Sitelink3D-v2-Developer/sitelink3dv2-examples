#!/usr/bin/python

# This example demonstrates the ability to download design data surveyed by an operator on a machine control client via the Design File service. Furthermore, 
# this service is used to perform a file format conversion to LANDXML. Device Design Data is stored within Sitelink3D v2 once it is pushed
# to the cloud and is accessed from the cloud using an RDM query with the view "v_op_files_by_operator". An RDM view is a named
# definition of the type of metadata being requested and how that data is keyed in the response.

import os
import sys
import itertools

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "file_download", "file_list", "file_features", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def main():
    arg_parser = argparse.ArgumentParser(description="Download operator pt3 files as landxml")

    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
    operator_domain_file_list = []
    more_data = True
    while more_data:
        params=page_traits.params()
        logging.debug("Using parameters:{}".format(json.dumps(params)))
        file_page = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="operator", a_view="v_op_files_by_operator", a_headers=headers, a_params=params)
        more_data = page_traits.more_data(file_page)
        logging.info ("Found {} items {}".format(len(file_page["items"]), "({})".format("unpaginated" if page_traits.page_number() == 1 else "last page") if not more_data else "(page {})".format(page_traits.page_number())))
        operator_domain_file_list.append(file_page["items"])
    operator_domain_file_list = list(itertools.chain.from_iterable(operator_domain_file_list))

    logging.info ("Found {} files in the 'operator' domain".format(len(operator_domain_file_list)))

    for fi in operator_domain_file_list:
        logging.debug(json.dumps(fi, sort_keys=True, indent=4))

    if len(operator_domain_file_list) == 0:
        sys.exit("")
    
    page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
    operator_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_operator_by_name", a_headers=headers, a_params=page_traits.params())

    operators = {}
    items_list = operator_list["items"]
    for item in items_list:
        operators[item["id"]] = "{} {} {}".format(item["value"]["firstName"], item["value"]["lastName"], item["id"])
    logging.debug(json.dumps(operators, indent=4))

    output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

    for fi in operator_domain_file_list:
        try:
            operator_output_dir = os.path.join(output_dir, operators[fi["value"]["operator"]])
        except KeyError:
            # perhaps the operator is archived, we can continue.
            continue
        download_dir = os.path.join(operator_output_dir, "downloaded")
        converted_dir = os.path.join(operator_output_dir, "converted")
        rdm_file_name = fi["value"]["name"]

        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(converted_dir, exist_ok=True)

        download_file(a_server_config=server, a_site_id=args.site_id, a_file_uuid=fi["value"]["sitelink_file_id"], a_headers=headers, a_target_dir=download_dir, a_target_name=rdm_file_name)

        features_to_import = query_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=fi["value"]["sitelink_file_id"], a_file_name=fi["value"]["name"], a_headers=headers)
        design_uuids = import_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=fi["value"]["sitelink_file_id"], a_file_name=fi["value"]["name"], a_features=features_to_import, a_headers=headers)

        for design_uuid in design_uuids:

            url = "{0}/designfile/v1/sites/{1}/design_files/{2}?design_type=Points&particular=LANDXML".format(server.to_url(), args.site_id, design_uuid)
            response = session.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            output_file = os.path.join(converted_dir, "{}.xml".format(os.path.splitext(rdm_file_name)[0]))
            with open(output_file, "wb") as handle:
                for data in tqdm(response.iter_content()):
                    handle.write(data)

if __name__ == "__main__":
    main()    

