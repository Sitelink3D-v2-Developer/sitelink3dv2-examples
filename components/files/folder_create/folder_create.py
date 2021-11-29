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

from get_token import *
from utils import *
from args import *

class FolderBean():
    def __init__(self, a_name, a_id, a_parent_uuid=None):
        self.name = a_name
        self.parent_uuid = a_parent_uuid
        if is_valid_uuid(a_id):
            self._id = str(a_id)
        else:
            self._id = str(uuid.uuid4())

    def to_json(self):
        ret = {
            "_id": self._id,
            "name" : self.name,
            "_rev":str(uuid.uuid1()),
            "_type":"fs::folder",
            "_at":int(round(time.time() * 1000))
        }
        if is_valid_uuid(self.parent_uuid):
            ret["parent"] = str(self.parent_uuid)
        return ret

def make_folder(a_folder_bean, a_server_config, a_site_id, a_headers):

    rdm_create_folder_url = "{0}/rdm_log/v1/site/{1}/domain/file_system/events".format(a_server_config.to_url(), a_site_id)

    logging.debug(json.dumps(a_folder_bean.to_json(), indent=4))
    data_encoded_json = {"data_b64": base64.b64encode(json.dumps(a_folder_bean.to_json()).encode('utf-8')).decode('utf-8')}
    response = session.post(rdm_create_folder_url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    logging.debug ("make-folder returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))
    if response.status_code == 200:
        logging.info("Folder created.")
    logging.debug ("The new folder uuid = {0}".format(a_folder_bean._id))



    # # Inserting into RDM is asyncronous. So we need to allow for a delay before checking.
    # # In production code, you should subscribe to the events service and respond appropriately.
    # time.sleep(1)

    rdm_filesystem_url = "{0}/rdm/v1/site/{1}/domain/file_system/view/_head".format(a_server_config.to_url(), a_site_id)
    limit, start = 1, base64.urlsafe_b64encode(json.dumps([a_folder_bean._id]).encode('utf-8')).decode('utf-8').rstrip("=")
    response = session.get(rdm_filesystem_url, headers=a_headers, params={"limit":limit,"start":start})
    response.raise_for_status()
    items = response.json()["items"]

    # validate payload
    found_data = False
    for item in items:
        logging.debug (item)
        if item["id"] == a_folder_bean._id:
            found_data = True
            break

    if False == found_data:
        logging.error("Could not find created directory")
        sys.exit(0)

    if items[0]["id"] != a_folder_bean._id: raise ValueError("folder _id=%s not found!" % (a_folder_bean._id))



def main():
    # >> Arguments
    arg_parser = argparse.ArgumentParser(description="Creating a Directory")

    # script parameters:
    arg_parser = add_arguments_logging(arg_parser, logging.INFO)

    # server parameters:
    arg_parser = add_arguments_environment(arg_parser)
    arg_parser = add_arguments_auth(arg_parser)

    # request parameters:
    arg_parser.add_argument("--site_id", default="", help="Site Identifier", required=True)
    arg_parser.add_argument("--folder_name", default="New Folder", help="Name for new folder")
    arg_parser.add_argument("--folder_uuid", default=str(uuid.uuid4()), help="UUID of folder")
    arg_parser.add_argument("--parent_uuid", default=None, help="UUID of parent")

    arg_parser.set_defaults()
    args = arg_parser.parse_args()
    logging.basicConfig(format=args.log_format, level=args.log_level)
    # << Arguments

    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

    logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
   
    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    folder_bean = FolderBean(a_name=args.folder_name, a_id=args.folder_uuid, a_parent_uuid=args.parent_uuid)

    make_folder(a_folder_bean=folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

if __name__ == "__main__":
    main()    
