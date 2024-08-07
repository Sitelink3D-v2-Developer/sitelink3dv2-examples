#!/usr/bin/env python

# This example demonstrates how files can be versioned and replaced in the Sitelink3D v2 file system.
#
# The following is an overview of this example:
# 1. Create a directory in the Sitelink3D v2 file system.
# 2. Upload the file found in the "version1" folder associated with this example.
# 3. Upload the file found in the "version2" folder associated with this example to replace the previous version.
# 4. List only files with more than one version.

import sys
import os

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "folder_create", "file_upload", "file_list", "rdm_list", "rdm_traits"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

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
file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name="example_file.txt", a_id=file_id, a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id, a_rev=file_ver1_uuid)
upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Uploading file version 2...")
# ------------------------------------------------------------------------------

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=example_file_ver2_path, a_file_name="example_file.txt")
file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name="example_file.txt", a_id=file_id, a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id, a_rev=file_ver2_uuid)
upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# Inserting into RDM is asyncronous. So we need to allow for a delay before checking.
time.sleep(0.5)

# ------------------------------------------------------------------------------
logging.info("Listing all files with more than one version...")
# ------------------------------------------------------------------------------

page_traits = RdmViewPaginationTraits(a_page_size="500", a_start="")
rj = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_view="v_fs_files_by_folder", a_headers=headers, a_params=page_traits.params())

for fi in rj["items"]:
    if fi["value"]["_type"] == "fs::file":

        # query the revision history for this file  
        page_traits = RdmViewPaginationTraits(a_page_size="500", a_start=[fi["id"]], a_end=[fi["id"],None])     
        ret = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_view="_hist", a_headers=headers, a_params=page_traits.params())

        if len(ret["items"]) > 1:
            logging.info("File {} {} has {} versions".format(fi["id"], fi["value"]["name"], len(ret["items"])))
