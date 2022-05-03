#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "get_token", "rdm_traits"]:
    exec(import_cmd(components_dir, imp))

session = requests.Session()

def create_task(a_server_config, a_site_id, a_task_name, a_headers, a_design_set_id=None):

    data_payload = TaskRdmTraits.post_bean_json(a_task_name, a_design_set_id)
    
    logging.debug("Task RDM payload: {}".format(json.dumps(data_payload, indent=4)))

    data_encoded_json = { "data_b64" : base64.b64encode(json.dumps(data_payload).encode('utf-8')).decode('utf-8') }
    url = "{0}/rdm_log/v1/site/{1}/domain/sitelink/events".format(a_server_config.to_url(),a_site_id)

    response = session.post(url, headers=a_headers, data=json.dumps(data_encoded_json))
    response.raise_for_status()    
    if response.status_code == 200:
        logging.info("Task created.")
        logging.debug ("create task returned {0}\n{1}".format(response.status_code, json.dumps(response.json(), indent=4)))
    else:  
        logging.info("Task creation unsuccessful. Status code {}: '{}'".format(response.status_code, response.text))
    
    return response.json()