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

from get_token      import *
from utils          import *
from folder_create  import *
from file_upload    import *
from file_features  import *
from file_list      import *
from datetime       import datetime

def query_rdm_view(a_server_config, a_domain, a_site_id, a_view, a_headers, a_limit=100):
    url = "{0}/rdm/v1/site/{1}/domain/{2}/view/{3}?limit={4}".format(a_server_config.to_url(), a_site_id, a_domain, a_view, a_limit)
    response = session.get(url, headers=a_headers)
    response.raise_for_status()
    return response.json()

def create_design_set(a_server_config, a_site_id, a_design_set_id, a_design_objects, a_headers):

    at = int(round(time.time() * 1000))

    data_payload = { "color" : "#077fdd",
        "designObjects" : design_objects_for_design_set,
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

def create_task(a_server_config, a_site_id, a_design_set_id, a_headers):

    at = int(round(time.time() * 1000))

    data_payload = { "activities":[],
        "design": { "alignment":{"locked":False},
                    "designObjectSets":[a_design_set_id],
                    "surface":{"locked":False}
                },
        "materials":{},
        "name":"%d API Task" % (at),
        "sequenceTypeClass":"none",
        "_rev":str(uuid.uuid4()),
        "_type":"sl::task",
        "_id": str(uuid.uuid4()),
        "_at":at
    }

    logging.debug("Task RDM payload: {}".format(json.dumps(data_payload, indent=4)))

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(data_payload).encode('utf-8')).decode('utf-8') }
    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(),a_site_id)

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()        
    return response.json()

# >> Arguments
arg_parser = argparse.ArgumentParser(description="Create a folder, upload a file, extract design data and create a task.")

# script parameters:
arg_parser.add_argument("--log_format", default='> %(asctime)-15s %(module)s %(levelname)s %(funcName)s:   %(message)s')
arg_parser.add_argument("--log_level", default=logging.INFO)

# server parameters:
arg_parser.add_argument("--dc", default="us", required=True)
arg_parser.add_argument("--env", default="", help="deploy environment (which determines server location)")
arg_parser.add_argument("--jwt", default="", help="jwt")
arg_parser.add_argument("--oauth_id", default="", help="oauth_id")
arg_parser.add_argument("--oauth_secret", default="", help="oauth_secret")
arg_parser.add_argument("--oauth_scope", default="", help="oauth_scope")

# request parameters:
arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)

arg_parser.set_defaults()
args = arg_parser.parse_args()
logging.basicConfig(format=args.log_format, level=args.log_level)
# << Arguments

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc)


header_json = {'content-type': 'application/json', 'X-Topcon-Auth': args.jwt}
if len(args.oauth_id) > 0 and len(args.oauth_secret) > 0 and len(args.oauth_scope) > 0:
    token = get_token(a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
    header_json = to_bearer_token_content_header(token["access_token"])
else:
    # ------------------------------------------------------------------------------
    logging.debug ("\nTesting token has not expired...")
    # ------------------------------------------------------------------------------
    try:
        # token is HEADER_B64.PAYLOAD_B64.SIGNATURE where HEADER_B64, PAYLOAD_B64 are base64-encoded json.
        # PAYLOAD['exp'] is the expiry time in seconds since epoch and we check it's in the future.
        payload_b64 = args.jwt.split(".")[1]              # fetch the second field
        payload_b64 += "=" * (-len(payload_b64) % 4)   # make sure it ends with enough padding chars
        payload_json = json.loads(base64.b64decode(payload_b64)) # cvt to json
        token_expiry = datetime.fromtimestamp(int(payload_json["exp"])) # get exp as a datetime
        time_now = datetime.now().replace(microsecond=0)                # get now as a datetime
        if token_expiry <= time_now:  raise ValueError("Token expired at %s (%s ago)" % (token_expiry.isoformat(' '), str(time_now-token_expiry)))
        if token_expiry.date() == time_now.date(): print (".. warning: token expires at {0} (in {1})".format(token_expiry.isoformat(' '), str(token_expiry-time_now)))
        else: print (".. ok: token expires at {0} (in {1})".format(token_expiry.isoformat(' '), str(token_expiry-time_now)))
    except Exception as e:
        print (".. ERROR: Token is invalid:", e)
        sys.exit(1)    

# << Server settings


server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))


# ------------------------------------------------------------------------------
logging.info("Creating a folder to upload files to...")
# ------------------------------------------------------------------------------

parent = None # Set this to the uuid of an existing folder to create a subfolder
folder_name = "{}-design-data-folder".format(int(round(time.time() * 1000)))
folder_bean = FolderBean(a_name=folder_name, a_id=uuid.uuid4(), a_parent_uuid=parent)

make_folder(a_folder_bean=folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=to_bearer_token_content_header(token["access_token"]))

logging.info("Uploading files to folder id={0} name={1}".format(folder_bean._id, folder_name))

# ------------------------------------------------------------------------------
logging.info("Uploading file containing design data ...")
# ------------------------------------------------------------------------------


file_upload_bean = FileUploadBean(a_site_identifier=args.site_id, a_upload_uuid=str(uuid.uuid4()), a_file_location=".", a_file_name="tps-bris.tp3")

file_rdm_bean = FileRdmBean(a_file_name="tps-bris.tp3", a_id=str(uuid.uuid4()), a_upload_uuid=str(file_upload_bean.upload_uuid), a_file_size=file_upload_bean.file_size, a_parent_uuid=folder_bean._id)

upload_file(a_file_upload_bean=file_upload_bean, a_file_rdm_bean=file_rdm_bean, a_server_config=server, a_site_id=args.site_id, a_headers=to_bearer_token_header(token["access_token"]), a_rdm_headers=to_bearer_token_content_header(token["access_token"]))


# ------------------------------------------------------------------------------
logging.info("Posting job to query file features (interrogate file for design objects):")
# ------------------------------------------------------------------------------

features_to_import = query_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=str(file_upload_bean.upload_uuid), a_file_name=file_rdm_bean.name, a_headers=to_bearer_token_content_header(token["access_token"]))

# ------------------------------------------------------------------------------
logging.info("Posting job to import the discovered features (design objects) from file:")
# ------------------------------------------------------------------------------

import_file_features(a_server_config=server, a_site_id=args.site_id, a_file_upload_uuid=str(file_upload_bean.upload_uuid), a_file_name=file_rdm_bean.name, a_features=features_to_import, a_headers=to_bearer_token_content_header(token["access_token"]))

# ------------------------------------------------------------------------------
logging.info("Listing design objects using RDM view:")
# ------------------------------------------------------------------------------
# Inserting into RDM is asyncronous. So we need to allow for a delay before checking.
# In production code, you should subscribe to the events service and respond appropriately.
time.sleep(0.5)


rj = query_rdm_view(a_server_config=server, a_domain="sitelink", a_site_id=args.site_id, a_view="v_sl_designObject_by_path", a_headers=to_bearer_token_content_header(token["access_token"]))

logging.debug("RDM view design objects by path of size {}: {}".format(len(rj["items"]), json.dumps(rj, indent=4)))



# ------------------------------------------------------------------------------
logging.info ("Create a new Design Set that references all imported design objects:")
# ------------------------------------------------------------------------------

design_objects_for_design_set = []
for i, design_object in enumerate(rj["items"]):
    design_objects_for_design_set.append(design_object["value"]["_id"])

design_set_id = str(uuid.uuid4())
rj = create_design_set(a_server_config=server, a_site_id=args.site_id, a_design_set_id=design_set_id, a_design_objects=design_objects_for_design_set, a_headers=to_bearer_token_content_header(token["access_token"]))


logging.debug ("Design Set RDM post returned\n{0}".format(json.dumps(rj,indent=4)))


# ------------------------------------------------------------------------------
logging.info ("Create a new Task that references the new Design Set:")
# ------------------------------------------------------------------------------


rj = create_task(a_server_config=server, a_site_id=args.site_id, a_design_set_id=design_set_id, a_headers=to_bearer_token_content_header(token["access_token"]))

logging.debug("Task RDM post returned\n{0}".format(json.dumps(rj,indent=4)))

logging.info("Done.")