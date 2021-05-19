#!/usr/bin/python
import logging
import os
import sys
import requests
import json
import base64
import uuid
import time

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "metadata"))

from metadata_traits import *

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
    logging.debug ("create auth code returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))