#!/usr/bin/python
import logging
import os
import sys
import json
import base64

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "file_download", "rdm_pagination_traits", "rdm_list", "transform", "site_detail"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()


def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id] )
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
 
    # First we determine whether this site is localised by searching for an RDM object with id "transform_gc3". This is
    # achieved by querying the _head of RDM rather than relying on a specific RDM view.
    rdm_view_list = GetTransform(a_server=server, a_site_id=args.site_id, a_headers=headers)

    localised = False
    transform_revision = ""
    for obj in rdm_view_list["items"]:
        try:
            if obj["id"] == "transform_gc3":
                localised = True
                transform_revision = obj["value"]["_rev"]
                logging.info("Found current site localisation file {} (version {})".format(obj["value"]["file"]["name"],transform_revision))
                break
        except KeyError:
            continue
    
    if localised:

        output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
        logging.debug(json.dumps(obj,indent=4))

        # Query and download all versions of the localization history at this site to a directory named as a function of the time the file was the active localization.
        page_traits = RdmViewPaginationTraits(a_page_size="500", a_start=["transform_gc3"], a_end=["transform_gc3",None])     
        ret = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="_hist", a_headers=headers, a_params=page_traits.params())

        logging.info("{} localization objects have been used at this site.".format(len(ret["items"])))
        for loc in ret["items"]:
            file_description = "transform file effective from timestamp {}".format(loc["value"]["_at"])
            logging.info("Downloading {}".format(file_description))
            target_dir = os.path.join(output_dir, file_description)
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, "metadata.json"),"w") as metadata_file:
                metadata_file.write(json.dumps(loc["value"], indent=4))
            download_file(a_server_config=server, a_site_id=args.site_id, a_file_uuid=loc["value"]["file"]["uuid"], a_headers=headers, a_target_dir=target_dir, a_target_name=loc["value"]["file"]["name"])

            for other_file in loc["value"]["other_files"]:
                download_file(a_server_config=server, a_site_id=args.site_id, a_file_uuid=other_file["uuid"], a_headers=headers, a_target_dir=target_dir, a_target_name=other_file["name"])

    else:
        logging.info("Site not localized.")

if __name__ == "__main__":
    main()    
