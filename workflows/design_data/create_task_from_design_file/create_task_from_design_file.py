#!/usr/bin/env python

# This example demonstrates a fundamental workflow in Sitelink3D v2. Tasks are RDM objects that are the selectable unit of work on a machine
# control client once it is connected to a site. Tasks are populated with a limited number of Design Sets; RDM objects that group together
# design data. This structure allows design objects to be organized semantically as desired. Curbing or pipework designs for example may occupy
# their own design set and can be included into one or more tasks so that machines needing to see that design work are able to access it in 
# a sensible manner. The organization of Design Sets and Tasks is flexible and entirely at the discretion of the site manager. Most machine
# control software, including the Topcon Haul App require at least one task to be defined at a site for selection.
#
# Design Objects represent the raw design data that is extracted from a design file. Design Objects are again RDM objects that are assigned 
# to Design Sets by linking their identifiers in the RDM object definition. This makes for a light weight association which is again flexible.
# The process of extracting design data from a design file is also demonstrated in this example. Two processing jobs are required to be applied
# after a design file has been uploaded and an associated RDM entry describing the file has been created.
#
# The first processing job queries the file to return the Design Objects contained within and the second processing job imports any or all of
# that returned set. Design Objects are stored in a generic container called the Global Data Set and from there can be linked into Design Sets
# for further linking into a Task for visibility on client software. 
#
# The following is an overview of this example:
# 1. Create a directory in the Sitelink3D v2 file system.
# 2. Upload a file specified by the file_name argument in the .bat or .sh wrapper script into that directory.
# 3. Create an RDM object representing that file so that it can be identified within Sitelink3D v2. Note that 2. and 3. are handled by the "upload_file" function.
# 4. Post a features query job to the Design File service using the "query_file_features" function to evaluate the design data available in the file.
# 5. Post an import job to the Design File service to extract the discovered features (or design data) from the file.
# 6. Create RDM representations for the imported features so they are represented within the system.
# 7. Create a new Design Set in RDM to bundle the imported features.
# 8. Create a new Task that references the Design Set.
#
# Note that an instructional video of this example is provided in the "videos" folder accompanying this example script.

import sys
import os
from datetime       import datetime

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "folder_create", "file_upload", "file_features", "file_list", "task_create", "rdm_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

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

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_file_name])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
logging.basicConfig(format=args.log_format, level=args.log_level)
logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

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

file_upload_bean = FileUploadBean(a_upload_uuid=str(uuid.uuid4()), a_file_location=".", a_file_name=args.file_name)
file_rdm_bean = FileRdmTraits.post_bean_json(a_file_name=args.file_name, a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id)

upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_domain="file_system", a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Posting job to query file features (interrogate file for design objects):")
# ------------------------------------------------------------------------------

features_to_import = query_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=str(file_upload_bean.upload_uuid), a_file_name=args.file_name, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Posting job to import the discovered features (design objects) from file:")
# ------------------------------------------------------------------------------

import_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=str(file_upload_bean.upload_uuid), a_file_name=args.file_name, a_features=features_to_import, a_headers=headers)

# ------------------------------------------------------------------------------
logging.info("Listing design objects using RDM view:")
# ------------------------------------------------------------------------------
# Inserting into RDM is asyncronous. So we need to allow for a delay before checking.
# In production code, you should subscribe to the events service and respond appropriately.
time.sleep(0.5)

page_traits = RdmViewPaginationTraits(a_page_size="500", a_start="")
rj = query_rdm_by_domain_view(a_server_config=server, a_site_id=args.site_id, a_domain="sitelink", a_view="v_sl_designObject_by_path", a_headers=headers, a_params=page_traits.params())

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