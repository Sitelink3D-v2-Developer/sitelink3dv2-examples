#!/usr/bin/env python

# ------------------------------------------------------------------------------
""" Create a Task from a file containing design data.

    This example performs the following at an existing Sitelink3D v2 site:
    - Creates a directory in the file system
    - Uploads a file into that directory
    - Posts a features query to evaluate the design data available in the file
    - Posts an import job to extract the discovered features from the file
    - Creates RDM representations for the imported features
    - Creates a new Design Set in RDM to bundle the imported features
    - Creates a new Task that references the Design Set

    The Task can be selected by Sitelink3D v2 clients connected to the site.
"""
# ------------------------------------------------------------------------------

import base64
import logging
import argparse
import json
import requests
import sys
import uuid
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "files", "folder_create"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "files", "file_upload"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "files", "file_features"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "files", "file_list"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "metadata", "metadata_create", "task_create"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "metadata", "metadata_list"))

from get_token      import *
from utils          import *
from folder_create  import *
from file_upload    import *
from file_features  import *
from file_list      import *
from task_create    import *
from datetime       import datetime
from args           import *
from metadata_traits import *
from metadata_list  import *

def create_design_set(a_server_config, a_site_id, a_design_set_id, a_design_objects, a_headers):

    if len(a_design_objects) > 64:
        logging.warning("Design Object list truncated to maximum Design Set size of 64.")
        del a_design_objects[64:] 
    
    at = int(round(time.time() * 1000))

    data_payload = { "color" : "#077fdd",
        "designObjects" : a_design_objects,
        "name":"%d API design set" % (at),
        "_rev":str(uuid.uuid4()),
        "_type":"sl::designObjectSet",
        "_id":a_design_set_id,
        "_at":at

    }

    logging.debug("Design Set RDM payload: {}".format(json.dumps(data_payload, indent=4)))

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(data_payload).encode('utf-8')).decode('utf-8') }
    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(),a_site_id)

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()

    return response.json()    


# >> Arguments
arg_parser = argparse.ArgumentParser(description="Create a folder, upload a file, extract design data and create a task.")

# script parameters:
arg_parser = add_arguments_logging(arg_parser, logging.INFO)

# server parameters:
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_auth(arg_parser)

# request parameters:
arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
arg_parser.add_argument("--design_file_name", default="", required=True)

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
folder_name = "{}-design-data-folder".format(int(round(time.time() * 1000)))
folder_bean = FolderBean(a_name=folder_name, a_id=uuid.uuid4(), a_parent_uuid=parent)

make_folder(a_folder_bean=folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

logging.info("Uploading files to folder id={0} name={1}".format(folder_bean._id, folder_name))

# ------------------------------------------------------------------------------
logging.info("Uploading file containing design data...")
# ------------------------------------------------------------------------------

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=".", a_file_name=args.design_file_name)
file_rdm_bean = FileMetadataTraits.post_bean_json(a_file_name=args.design_file_name, a_id=str(file_upload_bean.upload_uuid), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id)

upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Posting job to query file features (interrogate file for design objects):")
# ------------------------------------------------------------------------------

features_to_import = query_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=str(file_upload_bean.upload_uuid), a_file_name=args.design_file_name, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Posting job to import the discovered features (design objects) from file:")
# ------------------------------------------------------------------------------

import_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=str(file_upload_bean.upload_uuid), a_file_name=args.design_file_name, a_features=features_to_import, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Listing design objects using RDM view:")
# ------------------------------------------------------------------------------
# Inserting into RDM is asyncronous. So we need to allow for a delay before checking.
# In production code, you should subscribe to the events service and respond appropriately.
time.sleep(0.5)

page_traits = MetadataPaginationTraits(a_page_size="500", a_start="")
rj = query_metadata_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_designObject_by_path", a_headers=headers, a_params=page_traits.params())

logging.debug("RDM view design objects by path of size {}: {}".format(len(rj["items"]), json.dumps(rj, indent=4)))

# ------------------------------------------------------------------------------
logging.info ("Create a new Design Set that references all imported design objects:")
# ------------------------------------------------------------------------------

design_objects_for_design_set = []
for i, design_object in enumerate(rj["items"]):
    design_objects_for_design_set.append(design_object["value"]["_id"])

design_set_id = str(uuid.uuid4())
rj = create_design_set(a_server_config=server, a_site_id=args.site_id, a_design_set_id=design_set_id, a_design_objects=design_objects_for_design_set, a_headers=headers)


logging.debug ("Design Set RDM post returned\n{0}".format(json.dumps(rj,indent=4)))


# ------------------------------------------------------------------------------
logging.info ("Create a new Task that references the new Design Set:")
# ------------------------------------------------------------------------------

at = int(round(time.time() * 1000))
rj = create_task(a_server_config=server, a_site_id=args.site_id, a_task_name="%d API Task" % (at), a_headers=headers, a_design_set_id=design_set_id)

logging.debug("Task RDM post returned\n{0}".format(json.dumps(rj,indent=4)))

logging.info("Done.")