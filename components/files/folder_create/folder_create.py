#!/usr/bin/python
import os
import sys
import json

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
    else:  
        logging.info("Folder creation unsuccessful. Status code {}: '{}'".format(response.status_code, response.text))

    # Inserting into RDM is asynchronous so we need to allow for a delay before checking.
    # In production code, you should subscribe to the events service and respond appropriately before proceeding.
    #
    # We will now query RDM for details of the folder we just created to confirm that Sitelink3D v2 now knows about it.
    # The following code initialises the two parameters we will need to query RDM for information on the folder.
    # These are "start" and "limit".
    # 
    # The start parameter is a base64 encoded key list. In this example we specify a list with a single uuid as the start of the RDM search.
    # The limit parameter is set to one which produces only one result – confirming the existence of the folder just created only. 
    #
    # Produces the list containing the id of the folder that the example previously created as a string
    id_list_string = json.dumps([a_folder_bean._id])
    # eg: ["5ae193d3-f1a2-4330-83b5-fab3fb66b7fc"]

    # We send the key list on the wire base64 encoded and to perform that encoding, we need to convert the string into a byte array using
    id_list_bin = id_list_string.encode('utf-8') 
    # eg: b'["5ae193d3-f1a2-4330-83b5-fab3fb66b7fc"]'

    # which we can then pass to the encoder
    id_list_b64_bin = base64.urlsafe_b64encode(id_list_bin)
    # eg: b'WyI1YWUxOTNkMy1mMWEyLTQzMzAtODNiNS1mYWIzZmI2NmI3ZmMiXQ=='

    # The encoded byte array can be converted back to a string
    id_list_b64_string = id_list_b64_bin.decode('utf-8')
    # eg: WyI1YWUxOTNkMy1mMWEyLTQzMzAtODNiNS1mYWIzZmI2NmI3ZmMiXQ==

    # We are then able to strip the byte padding from the base64 encoded string with 
    id_list_b64_string_stripped = id_list_b64_string.rstrip("=")
    # eg: WyI1YWUxOTNkMy1mMWEyLTQzMzAtODNiNS1mYWIzZmI2NmI3ZmMiXQ

    # which then forms part of the complete request
    limit, start = 1, id_list_b64_string_stripped
    rdm_filesystem_url = "{0}/rdm/v1/site/{1}/domain/file_system/view/_head".format(a_server_config.to_url(), a_site_id)
    
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
    script_name = os.path.basename(os.path.realpath(__file__))

    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_folder_name, arg_folder_uuid, arg_folder_parent_uuid])
    # << Argument handling

    # >> Server & logging configuration
    server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
    logging.basicConfig(format=args.log_format, level=args.log_level)
    logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
    # << Server & logging configuration

    headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

    folder_bean = FolderBean(a_name=args.folder_name, a_id=args.folder_uuid, a_parent_uuid=args.folder_parent_uuid)

    make_folder(a_folder_bean=folder_bean, a_server_config=server, a_site_id=args.site_id, a_headers=headers)

if __name__ == "__main__":
    main()    
