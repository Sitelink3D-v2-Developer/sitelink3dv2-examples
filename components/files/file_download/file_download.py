#!/usr/bin/python
import os
import sys
from tqdm import tqdm

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_traits", "rdm_list", "rdm_pagination_traits"]:
    exec(import_cmd(components_dir, imp))


session = requests.Session()

# This helper function does the work of downloading a file from Sitelink3D v2. Downloading a file is comprised of 
# streaming the file contents provided by a GET call made to the file microservice and writing to the local file system.
# 
# A file ID is used to identify the file to download. The file ID can be determined when a file is uploaded 
# (see https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples/tree/main/components/files/file_upload) or 
# by listing the available files at a site 
# (see https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples/tree/main/components/files/file_list).
# 
# See https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-api-documentation/blob/master/services/chapter3_files.md 
# for more information about files in Sitelink3D v2. 
def download_file(a_server_config, a_site_id, a_file_uuid, a_headers, a_target_dir="", a_target_name=""):

    get_file_url = "{0}/file/v1/sites/{1}/files/{2}/url".format(a_server_config.to_url(), a_site_id, a_file_uuid)

    # get the url of the file
    response = session.get(get_file_url, headers=a_headers)
    response.raise_for_status()

    # get the content of the url
    url = "{0}{1}".format(a_server_config.to_url(), response.text)
    logging.debug("get file {0} by url {1}".format(a_file_uuid, url))
    response = session.get(url, headers=a_headers, stream=True)
    response.raise_for_status()

    output_name = a_target_name
    if len(output_name) == 0:
        output_name = a_file_uuid

    output_dir = a_target_dir
    if len(output_dir) == 0:
        output_dir = make_site_output_dir(a_server_config=a_server_config, a_headers=a_headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=a_site_id)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_file = os.path.join(output_dir, output_name)
    with open(output_file, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)


def main():
    script_name = os.path.basename(os.path.realpath(__file__))
    
    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_file_uuid, arg_file_id])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    # >> Authorization
    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    # << Authorization

    # Fetch the name of the file in RDM if we've been provided a file_id parameter so that we can name the file we download to the local file system as it is named in RDM
    target_name = args.file_uuid
    if len(args.file_id) > 0:

        page_traits = RdmPaginationTraits(a_page_size="500", a_start=[args.file_id], a_end=[args.file_id, None])
        rj = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_view="_head", a_headers=headers, a_params=page_traits.params())
        if len(rj["items"]) > 0:
            target_name = rj["items"][0]["value"]["name"] # There should be only one entry as we specified a unique ID
                
    target_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
    download_file(a_server_config=server, a_site_id=args.site_id, a_file_uuid=args.file_uuid, a_headers=headers, a_target_dir=target_dir, a_target_name=target_name)


if __name__ == "__main__":
    main()    

