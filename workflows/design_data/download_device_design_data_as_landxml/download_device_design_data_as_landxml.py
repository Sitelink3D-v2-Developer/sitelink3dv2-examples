#!/usr/bin/python

# This example demonstrates the ability to download design data surveyed on machine control clients via the Design File service. Furthermore, 
# this service is used to perform a file format conversion to LANDXML. Device Design Data is stored within Sitelink3D v2 once it is pushed
# to the cloud and is accessed from the cloud using an RDM query with the view "v_sl_deviceDesignObject_by_deviceURN". An RDM view is a named
# definition of the type of metadata being requested and how that data is keyed in the response.

import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "site_detail", "get_token", "file_download", "file_list", "file_features", "rdm_list"]:
    exec(import_cmd(components_dir, imp))
 
session = requests.Session()

def particular_from_design_type(a_design_type):
    if(a_design_type == "Lines"):
        return "LN3"
    elif(a_design_type == "Planes"):
        return "PL3"
    elif(a_design_type == "Points"):
        return "PT3"
    elif(a_design_type == "Roads"):
        return "RD3"
    elif(a_design_type == "Surfaces"):
        return "TN3"
    else:
        return "Invalid"

def main():

    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_pagination_page_limit, arg_pagination_start])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id,
                                        a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    page_traits = RdmViewPaginationTraits(a_page_size=args.page_limit, a_start=args.start)
    device_design_object_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink",
                                                              a_view="v_sl_deviceDesignObject_by_deviceURN", a_headers=headers, a_params=page_traits.params())["items"]

    logging.info("Found {} device design objects".format(len(device_design_object_list)))
    for fi in device_design_object_list:
        logging.debug(json.dumps(fi, sort_keys=True, indent=4))

    output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

    for fi in device_design_object_list:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        device_output_dir = os.path.join(output_dir, fi["value"]["deviceURN"].replace(':', "-"))
        original_dir = os.path.join(device_output_dir, "original")
        converted_dir = os.path.join(device_output_dir, "converted")
        rdm_file_name = fi["value"]["name"]

        os.makedirs(original_dir, exist_ok=True)
        os.makedirs(converted_dir, exist_ok=True)

        particular = particular_from_design_type(fi["value"]["designType"])
        base = "{}/designfile/v1/sites/{}/design_files/{}?design_type={}&particular=".format(
            server.to_url(), args.site_id, fi["value"]["doFileUUID"], fi["value"]["designType"])
        url_original = ["{}{}".format(base, particular), particular.lower(), original_dir]
        url_landxml = ["{}LANDXML".format(base), "xml", converted_dir]
        for url, ext, target in [url_original, url_landxml]:
            response = session.get(url, headers=headers, stream=True)
            response.raise_for_status()

            output_file = os.path.join(target, "{}.{}".format(
                os.path.splitext(rdm_file_name)[0], ext))
            with open(output_file, "wb") as handle:
                for data in tqdm(response.iter_content()):
                    handle.write(data)

if __name__ == "__main__":
    main()
