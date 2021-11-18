#!/usr/bin/env python

import logging
import argparse
import requests
import sys
import uuid
import os
import json

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
from metadata_list  import *


# >> Arguments
arg_parser = argparse.ArgumentParser(description=os.path.basename(os.path.realpath(__file__)))

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
logging.info("Creating root folder to upload files to...")
# ------------------------------------------------------------------------------

root_folder_name = "{}-folder-hierarchy-root".format(int(round(time.time() * 1000)))
root_folder_bean = FolderBean(a_name=root_folder_name, a_id=uuid.uuid4(), a_parent_uuid=None)

make_folder(a_folder_bean=root_folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

logging.info("Uploading level 1 file to folder id={0} name={1}".format(root_folder_bean._id, root_folder_name))

# ------------------------------------------------------------------------------

current_dir = os.path.dirname(os.path.realpath(__file__))
root_folder_path = os.path.join(current_dir, "folder_root")

level_1_file_uuid = str(uuid.uuid4())

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=root_folder_path, a_file_name="level_1_file.txt")
file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name="level_1_file.txt", a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=root_folder_bean._id, a_rev=level_1_file_uuid)
upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

level_1_folder_name = "level_1_folder"
level_1_folder_bean = FolderBean(a_name=level_1_folder_name, a_id=uuid.uuid4(), a_parent_uuid=root_folder_bean._id)

make_folder(a_folder_bean=level_1_folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Uploading level 2 file to folder id={0} name={1}".format(level_1_folder_bean._id, level_1_folder_name))
# ------------------------------------------------------------------------------

level_2_file_uuid = str(uuid.uuid4())
level_1_folder_path = os.path.join(root_folder_path, "level_1_folder")

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=level_1_folder_path, a_file_name="level_2_file.txt")
file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name="level_2_file.txt", a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=level_1_folder_bean._id, a_rev=level_2_file_uuid)
upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

level_2_folder_name = "level_2_folder"
level_2_folder_bean = FolderBean(a_name=level_2_folder_name, a_id=uuid.uuid4(), a_parent_uuid=level_1_folder_bean._id)

make_folder(a_folder_bean=level_2_folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Listing only files and folders under root directory just created...")
# ------------------------------------------------------------------------------

files_and_folders = query_nested_files_and_folders(a_server_config=server, a_site_id=args.site_id, a_parent_folder_uuid=root_folder_bean._id, a_headers=headers)
logging.info("Found {} files and folders in the specified directory.".format(len(files_and_folders)))
for fi in files_and_folders:
    logging.debug(json.dumps(fi, indent=4))
