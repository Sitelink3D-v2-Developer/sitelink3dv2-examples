#!/usr/bin/python
import logging
import os
import sys
import requests
import base64

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["metadata_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def create_auth_code(a_server_config, a_site_id, a_code_name, a_code_pin, a_headers, a_valid_days=1):

    auth_code_rdm_bean = AuthCodeMetadataTraits.post_bean_json(a_code_name=a_code_name, a_code_pin=a_code_pin, a_valid_days=a_valid_days)

    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(), a_site_id)
    logging.debug ("Upload RDM to {}".format(url))
    
    json.dumps(auth_code_rdm_bean,indent=4)

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(auth_code_rdm_bean).encode('utf-8')).decode('utf-8') }
    logging.debug("Delay RDM payload: {}".format(json.dumps(auth_code_rdm_bean, indent=4)))

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    if response.status_code == 200:
        logging.info("Auth Code created.")
    logging.debug ("create auth code returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))