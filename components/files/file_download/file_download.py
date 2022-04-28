#!/usr/bin/python
import os
import sys
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))

from get_token import *
from utils import *
from args import *

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
        current_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(current_dir, a_site_id)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_file = os.path.join(output_dir, output_name)
    with open(output_file, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)


def main():
    script_name = os.path.basename(os.path.realpath(__file__))
    
    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_file_uuid])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    # >> Authorization
    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    # << Authorization

    download_file(a_server_config=server, a_site_id=args.site_id, a_file_uuid=args.file_uuid, a_headers=headers)

if __name__ == "__main__":
    main()    

