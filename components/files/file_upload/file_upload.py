#!/usr/bin/python
import argparse
import logging
import os
import sys
import requests
import json
import base64
import uuid
import time

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "metadata"))

from get_token import *
from utils import *
from metadata_traits import *
from args import *


session = requests.Session()

class FileUploadBean:
    def __init__(self,a_site_identifier, a_upload_uuid, a_file_location, a_file_name):
        if is_valid_uuid(a_upload_uuid):
            self.upload_uuid = str(a_upload_uuid)
        else:
            self.upload_uuid = str(uuid.uuid4())
        self.file_location = a_file_location
        self.file_name = a_file_name
        self.file_size = os.path.getsize(a_file_location + os.path.sep + a_file_name)

    def to_json(self):
        full_path = self.file_location + os.path.sep + self.file_name
        return {
            "upload-uuid": str(self.upload_uuid),
            "upload-file-name" : self.file_name,
            "upload-file-size" : self.file_size,
        }

def upload_file(a_file_upload_bean, a_file_rdm_bean, a_server_config, a_site_id, a_domain, a_headers, a_rdm_headers):

    with open(a_file_upload_bean.file_location + os.path.sep + a_file_upload_bean.file_name, 'rb') as file_ptr:
        files = { "upload-file" : file_ptr}
        url = "{0}/file/v1/sites/{1}/upload".format(a_server_config.to_url(), a_site_id)
        logging.debug ("Upload file to {}".format(url))
        logging.debug("File Upload payload: {}".format(json.dumps(a_file_upload_bean.to_json(), indent=4)))

        response = session.post(url, headers=a_headers, params=a_file_upload_bean.to_json(), files=files)
        response.raise_for_status()

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(a_file_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("File RDM payload: {}".format(json.dumps(a_file_rdm_bean, indent=4)))

    
    url = "{0}/rdm_log/v1/site/{1}/domain/{2}/events".format(a_server_config.to_url(), a_site_id, a_domain)
    logging.debug ("Upload RDM to {}".format(url))
    
    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    logging.debug ("upload_file returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))


def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Upload a file.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    arg_parser.add_argument("--file_name", default="", required=True)
    arg_parser.add_argument("--file_uuid", default=str(uuid.uuid4()), help="UUID of file")
    arg_parser.add_argument("--parent_uuid", default=None, help="UUID of parent")
    arg_parser.add_argument("--domain", default="file_system", help="The purpose of the file - file_system or operator")

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
   
    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server, a_content_type="")
    headers_json_content = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    file_upload_bean = FileUploadBean(a_site_identifier=args.site_id, a_upload_uuid=args.file_uuid, a_file_location=".", a_file_name=os.path.basename(args.file_name))

    file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name=args.file_name, a_id=file_upload_bean.upload_uuid, a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_domain=args.domain, a_parent_uuid=args.parent_uuid)

    upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain=args.domain, a_headers=headers, a_rdm_headers=headers_json_content)
   

if __name__ == "__main__":
    main()    
