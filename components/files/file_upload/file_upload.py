#!/usr/bin/python
import os
import sys
import math
from requests_toolbelt import (MultipartEncoder, MultipartEncoderMonitor)

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "get_token", "rdm_traits"]:
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
#
# Sitelink3D v2 will reject file uploads larger than 10485760 bytes. In these cases, the repsponse will be of the form 
# 400:{"success":false,"error":"Upload size (41455634) exceeds maximum size (10485760) for a single part upload","preventRetry":false}
# For this reason, multi-part uploads should be used for files in excess of this size. This is demonstrated in the below example.
#
class FileUploadBean:
    def __init__(self, a_upload_uuid, a_file_location, a_file_name):
        if is_valid_uuid(a_upload_uuid):
            self.upload_uuid = str(a_upload_uuid)
        else:
            self.upload_uuid = str(uuid.uuid4())
        self.file_location = a_file_location
        self.file_name = a_file_name
        self.file_size = os.path.getsize(a_file_location + os.path.sep + a_file_name)

SITELINK_MAX_PART_SIZE = 10485760

# Yield parts of data from file pointer until EOF. This avoids reading large files completely into memory.
# This function is used to chunk the data if its size exceeds the maximum part size accpeted by the 
# Sitelink3D v2 file service (and other services that accept file such as designfile)
def read_parts(a_file_ptr, a_part_size=SITELINK_MAX_PART_SIZE):
    while True:
        part = a_file_ptr.read(a_part_size)
        if not part:
            break
        yield part 

def upload_file_multipart(a_server_config, a_site_id, a_file_upload_bean, a_headers):
    url = "{0}/file/v1/sites/{1}/upload".format(a_server_config.to_url(), a_site_id)
    logging.debug("Upload file to {}".format(url))

    file_path = a_file_upload_bean.file_location + os.path.sep + a_file_upload_bean.file_name
    part_index = 0
    part_generator = read_parts(a_file_ptr=open(file_path, "rb"), a_part_size=SITELINK_MAX_PART_SIZE)

    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        sha1.update(f.read())

    digest = sha1.hexdigest()

    for part in part_generator:
        part_total_count = math.ceil(a_file_upload_bean.file_size / SITELINK_MAX_PART_SIZE)

        logging.debug("Preparing data part index {} of {} (size {})".format(part_index, part_total_count, len(part)))

        form_header = {
            "upload-uuid": str(a_file_upload_bean.upload_uuid),
            "upload-file-name": a_file_upload_bean.file_name,
            "upload-file-sha1": digest,
            "upload-file-size": str(a_file_upload_bean.file_size),
            "upload-part-index": str(part_index),
            "upload-total-parts": str(part_total_count),
            "upload-part-size": str(len(part)),
            "upload-file" : (a_file_upload_bean.file_name, part, "application/octet-stream")
        }

        multipartEncoder = MultipartEncoder(fields=form_header)
        headers = a_headers
        headers["Content-Type"]="multipart/form-data; boundary={}".format(multipartEncoder.boundary_value)

        response = requests.post(url, headers=headers, data=multipartEncoder)
        logging.info("File part upload returned {}:{}".format(response.status_code, response.text))
        part_index = part_index + 1


def upload_file(a_file_upload_bean, a_file_rdm_bean, a_server_config, a_site_id, a_domain, a_headers):

    upload_file_multipart(a_server_config, a_site_id, a_file_upload_bean, a_headers)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(a_file_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("File RDM payload: {}".format(json.dumps(a_file_rdm_bean, indent=4)))

    url = "{0}/rdm_log/v1/site/{1}/domain/{2}/events".format(a_server_config.to_url(), a_site_id, a_domain)
    logging.debug ("Upload RDM to {}".format(url))
    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    logging.debug("upload_file returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))

    if response.status_code == 200:
        logging.info("File uploaded.")
    else:  
        logging.info("File upload unsuccessful. Status code {}: '{}'".format(response.status_code, response.text))

def main():
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_file_name, arg_file_parent_uuid, arg_rdm_domain_default_filesystem])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=".", a_file_name=os.path.basename(args.file_name))

    file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name=args.file_name, a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_domain=args.rdm_domain, a_parent_uuid=args.file_parent_uuid)

    upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain=args.rdm_domain, a_headers=headers)
   

if __name__ == "__main__":
    main()    
