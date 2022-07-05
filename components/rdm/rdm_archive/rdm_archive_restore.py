#!/usr/bin/python
import os
import sys
import json
import base64
from uuid import uuid4
import logging

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "utils"))

from get_token import *
from utils import *
from args import *

session = requests.Session()

def archive_rdm_object(a_rdm_object_bean, a_domain, a_server_config, a_site_id, a_headers):
    set_rdm_object_archive_flag(a_rdm_object_bean, a_domain, True, a_server_config, a_site_id, a_headers)

def restore_rdm_object(a_rdm_object_bean, a_domain, a_server_config, a_site_id, a_headers):
    set_rdm_object_archive_flag(a_rdm_object_bean, a_domain, False, a_server_config, a_site_id, a_headers)

def set_rdm_object_archive_flag(a_rdm_object_bean, a_domain, a_archive_flag, a_server_config, a_site_id, a_headers):

    url = "{0}/rdm_log/v1/site/{1}/domain/{2}/events".format(a_server_config.to_url(), a_site_id, a_domain)
    
    a_rdm_object_bean["_archived"] = a_archive_flag
    a_rdm_object_bean["_rev"] = str(uuid4())
    a_rdm_object_bean["_at"] = int(round(time.time() * 1000))
    logging.debug(json.dumps(a_rdm_object_bean,indent=4))

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(a_rdm_object_bean).encode('utf-8')).decode('utf-8') }

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()
    if response.status_code == 200:
        operation = "archived" if a_archive_flag else "restored"
        try:
            logging.info("Object {} ({}) {}.".format(a_rdm_object_bean["name"], a_rdm_object_bean["_id"], operation ))
        except KeyError:
            logging.info("Object archived.")
    else: 
        operation = "archival" if a_archive_flag else "restoration"
        try: 
            logging.info("Object {} ({}) archival unsuccessful. Status code {}: '{}'".format(a_rdm_object_bean["name"], a_rdm_object_bean["_id"], response.status_code, response.text))
        except KeyError:
            logging.info("Object {} unsuccessful. Status code {}: '{}'".format(operation, response.status_code, response.text))

