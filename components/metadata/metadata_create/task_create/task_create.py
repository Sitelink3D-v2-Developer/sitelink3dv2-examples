#!/usr/bin/python
import logging
import os
import sys
import requests
import json
import base64
import uuid
import time

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "metadata"))

from get_token import *
from utils import *
from metadata_traits import *


session = requests.Session()

def create_task(a_server_config, a_site_id, a_task_name, a_headers, a_design_set_id=None):

    data_payload = TaskMetadataTraits.post_bean_json(a_task_name, a_design_set_id)
    
    logging.debug("Task RDM payload: {}".format(json.dumps(data_payload, indent=4)))

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(data_payload).encode('utf-8')).decode('utf-8') }
    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(),a_site_id)

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()        
    return response.json()