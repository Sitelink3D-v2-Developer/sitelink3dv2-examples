#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "file_download", "file_list", "file_features", "rdm_list"]:
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
    arg_parser = argparse.ArgumentParser(
        description="Download device design files as landxml")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    arg_parser = add_arguments_pagination(arg_parser)

    # request parameters:
    arg_parser = add_arguments_site(arg_parser)

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(
        os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id,
                                        a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    page_traits = RdmPaginationTraits(a_page_size="500", a_start="")
    device_design_object_list = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink",
                                                              a_view="v_sl_deviceDesignObject_by_deviceURN", a_headers=headers, a_params=page_traits.params())["items"]

    logging.info("Found {} device design objects".format(
        len(device_design_object_list)))
    for fi in device_design_object_list:
        logging.debug(json.dumps(fi, sort_keys=True, indent=4))

    for fi in device_design_object_list:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(
            current_dir, args.site_id[0:12], fi["value"]["deviceURN"].replace(':', "-"))
        original_dir = os.path.join(output_dir, "original")
        converted_dir = os.path.join(output_dir, "converted")
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
