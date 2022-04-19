#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "get_token", "metadata_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

# The act of uploading a file is represented by the upload_uuid field in this FileUploadBean bean.
# This uuid internally represents the upload blobs as they happen and allows the specific instance 
# of a file upload to be referenced later.
# 
# Referencing specific upload_uuid instances is useful when:
# 1. Querying an uploaded file for its design data contents; see query_file_features function.
# 2. Linking design objects in RDM to the particular file upload that created them; see import_file_features function.
#
# Multiple uploads of the same file are represented by different upload_uuids.
# This is the mechanism by which file versioning is achieved.
#
# Because the FileUploadbean is the start of the upload_uuid chain, it is generated on creation rather than passsed in as a client parameter.
class FileUploadBean:
    def __init__(self, a_upload_uuid, a_file_location, a_file_name):
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

def upload_file(a_file_upload_bean, a_file_rdm_bean, a_server_config, a_site_id, a_domain, a_headers):

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
    logging.debug ("upload_file returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))

    if response.status_code == 200:
        logging.info("File uploaded.")

def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Upload a file.")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    arg_parser.add_argument("--file_name", default="", required=True)
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

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=".", a_file_name=os.path.basename(args.file_name))

    file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name=args.file_name, a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_domain=args.domain, a_parent_uuid=args.parent_uuid)

    upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain=args.domain, a_headers=headers)
   

if __name__ == "__main__":
    main()    
