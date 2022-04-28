#!/usr/bin/env python

# This example demonstrates how files and folders in a hierarchy can be uploaded to the Sitelink3D v2 file system.
#
# The following is an overview of this example:
# 1. Create a directory in the Sitelink3D v2 file system.
# 2. Work through the "folder_root" directory associated with this script, uploading files and folders to the created directory.
# 3. List only files and folders uploaded under the root directory just created, ignoring other files and folders that may already exist.

import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "folder_create", "file_upload", "file_list", "rdm_list", "rdm_traits"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=args.log_level)
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

# ------------------------------------------------------------------------------
logging.info("Creating root folder to upload files to...")
# ------------------------------------------------------------------------------

root_folder_name = "{}-folder-hierarchy-root".format(int(round(time.time() * 1000)))
root_folder_bean = FolderBean(a_name=root_folder_name, a_id=uuid.uuid4(), a_parent_uuid=None)

make_folder(a_folder_bean=root_folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Uploading level 1 file to folder id={0} name={1}".format(root_folder_bean._id, root_folder_name))
# ------------------------------------------------------------------------------

current_dir = os.path.dirname(os.path.realpath(__file__))
root_folder_path = os.path.join(current_dir, "folder_root")

level_1_file_uuid = str(uuid.uuid4())

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=root_folder_path, a_file_name="level_1_file.txt")
file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name="level_1_file.txt", a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=root_folder_bean._id, a_rev=level_1_file_uuid)
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
file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name="level_2_file.txt", a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=level_1_folder_bean._id, a_rev=level_2_file_uuid)
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
