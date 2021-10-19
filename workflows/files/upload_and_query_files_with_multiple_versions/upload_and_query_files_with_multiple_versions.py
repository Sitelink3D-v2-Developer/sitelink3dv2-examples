#!/usr/bin/env python

import logging
import argparse
import requests
import sys
import uuid
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "files", "folder_create"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "files", "file_upload"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "files", "file_list"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "metadata", "metadata_list"))

from get_token      import *
from utils          import *
from folder_create  import *
from file_upload    import *
from file_list      import *
from datetime       import datetime
from args           import *
from metadata_traits import *
from metadata_list import *


# >> Arguments
arg_parser = argparse.ArgumentParser(description="Demonstrate how multiple versions of the same file are managed.")

# script parameters:
arg_parser = add_arguments_logging(arg_parser, logging.INFO)

# server parameters:
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_auth(arg_parser)

# request parameters:
arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)

arg_parser.set_defaults()
args = arg_parser.parse_args()
logging.basicConfig(format=args.log_format, level=args.log_level)
# << Arguments

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

# << Server settings

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

# ------------------------------------------------------------------------------
logging.info("Creating a folder to upload files to...")
# ------------------------------------------------------------------------------

parent = None # Set this to the uuid of an existing folder to create a subfolder
folder_name = "{}-file-version-folder".format(int(round(time.time() * 1000)))
folder_bean = FolderBean(a_name=folder_name, a_id=uuid.uuid4(), a_parent_uuid=parent)

make_folder(a_folder_bean=folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

logging.info("Uploading files to folder id={0} name={1}".format(folder_bean._id, folder_name))

# ------------------------------------------------------------------------------
logging.info("Uploading file version 1...")
# ------------------------------------------------------------------------------

current_dir = os.path.dirname(os.path.realpath(__file__))
example_file_ver1_path = os.path.join(current_dir, "version1")
example_file_ver2_path = os.path.join(current_dir, "version2")

file_id = str(uuid.uuid4())
file_ver1_uuid = str(uuid.uuid4())
file_ver2_uuid = str(uuid.uuid4())

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=example_file_ver1_path, a_file_name="example_file.txt")
file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name="example_file.txt", a_id=file_id, a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id, a_rev=file_ver1_uuid)
upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Uploading file version 2...")
# ------------------------------------------------------------------------------

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=example_file_ver2_path, a_file_name="example_file.txt")
file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name="example_file.txt", a_id=file_id, a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id, a_rev=file_ver2_uuid)
upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# Inserting into RDM is asyncronous. So we need to allow for a delay before checking.
time.sleep(0.5)

# ------------------------------------------------------------------------------
logging.info("Listing all files with more than one version...")
# ------------------------------------------------------------------------------

page_traits = MetadataPaginationTraits(a_page_size="500", a_start="")
rj = query_metadata_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_view="v_fs_files_by_folder", a_headers=headers, a_params=page_traits.params())

for fi in rj["items"]:
    if fi["value"]["_type"] == "fs::file":

        # query the revision history for this file  
        page_traits = MetadataPaginationTraits(a_page_size="500", a_start=[fi["id"]], a_end=[fi["id"],None])     
        ret = query_metadata_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_view="_hist", a_headers=headers, a_params=page_traits.params())

        if len(ret["items"]) > 1:
            logging.info("File {} {} has {} versions".format(fi["id"], fi["value"]["name"], len(ret["items"])))

