#!/usr/bin/env python

import argparse
from email import header
from platform import machine
import requests
import logging
import json
import logging
import os
import sys
import datetime
import base64
from dateutil import tz

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "mfk"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "tokens"))

from get_token      import *
from utils          import *
from args           import *
from mfk            import *

# Configure Arguments
arg_parser = argparse.ArgumentParser(description="Read historical data from the datalogger microservice.")
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_logging(arg_parser, logging.INFO)
arg_parser = add_arguments_site(arg_parser)
arg_parser = add_arguments_auth(arg_parser)
arg_parser.add_argument("--startms", default="", help="Start of data ms since epoch", required=True)
arg_parser.add_argument("--endms", default="", help="End of data ms since epoch", required=True)
arg_parser.add_argument("--report_file_name", default="", help="File to write datalogger output to", required=True)

arg_parser.set_defaults()
args = arg_parser.parse_args()

# Configure Logging
logger = logging.getLogger("datalogger")
logging.basicConfig(format=args.log_format, level=args.log_level)

# >> Server settings
session = requests.Session()

server_https = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")

logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server_https.to_url(), args.dc, args.site_id))

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server_https)

logging.debug(headers)
dba_url = "{}/dba/v1/sites/{}/updates?startms={}&endms={}&category=low_freq".format(server_https.to_url(), args.site_id, args.startms, args.endms)
logging.debug("dba_url: {}".format(dba_url))

# get the data
response = session.get(dba_url, headers=headers)
logging.debug(response.text)
response.raise_for_status()

resources = {}
assets = {}
state = {}

logging.info("Writing report to {}".format(args.report_file_name))
report_file = open(args.report_file_name, "w")

report_file.write("Machine ID, Device ID, Machine Name, Time (UTC), GPS Mode, MC Mode, Speed (km/h), Reverse, Delay Id, Operator Id, Task Id, Left X, Left Y, Left Z, Right X, Right Y, Right Z")

def GetPointOfInterestLocalSpace(a_component, a_point_of_interest):
    
    transform_interface = a_component.interfaces["transform"]
    points_of_interest_interface = a_component.interfaces["points_of_interest"]

    poi = next((sub for sub in points_of_interest_interface.points if sub.id == a_point_of_interest), None)  
    logging.debug("Using Point {}".format(poi))
    node = a_component.get_interface_object("topcon.nodes.blade")
    logging.debug("Using Node {}".format(node))
    node_transform = node.get_local_transform()

    # We want to multiple the POI's referenced (and pre-transformed) node by the POI's offset.
    # In this example, the point is blade left or blade right.
    # When processing replicates they're applied to a transform in the node (referenced by the point of interest) that's already been local transformed because UpdateTransform was already called in the MFK SDK.
    poi_offset = poi.get_point()
    transformed_offset_point =  node_transform * poi_offset

    # Each time a replicate comes in, point.GetNode().GetTransform() is getting that pre-transformed node and then applying this offset from the point (which is the point of interest offset apart from its parent transform).
    # Remember that a point of interest has a parent node (node reference).
    # That puts the point of interest in the correct local space relative to the root. 
    machine_to_local_transform = transform_interface.get_transform()

    # the transformed offset point is then multiplied by the machine to local transform to get the actual world space n,e,z
    poi_local_space = machine_to_local_transform * transformed_offset_point

    logging.debug("POI in local space {}".format(poi_local_space))

    return poi_local_space

def OutputLineItem(a_file_ptr, a_replicate, a_position_info, a_auto_grade_control, a_reverse, a_blade_left, a_blade_right, a_state={}):
    ac_uuid = a_replicate["data"]["ac_uuid"]
    machine_name = "-"
    device_id = "-"
    operator_id = "-"
    task_id = "-"
    delay_id = "-"

    try:
        operator_id = a_state["topcon.rdm.list"]["operator"]["value"]
    except KeyError:
        logging.debug("No Operator state found.")

    try:
        operator_id = a_state["topcon.rdm.list"]["delay"]["value"]
    except KeyError:
        logging.debug("No Delay state found.")

    try:
        task_id = a_state["topcon.task"]["id"]["value"]
    except KeyError:
        logging.debug("No Task state found.")
        

    for i, val in enumerate(assets[ac_uuid]["signatures"]):
        if val["asset_urn"].startswith("urn:X-topcon:machine"):
            machine_name = val["asset_urn"].split(":")[-1]

        if val["asset_urn"].startswith("urn:X-topcon:device"):
            device_id = val["asset_urn"].split(":")[-1]
    
    utc_time = datetime.datetime.fromtimestamp(a_replicate["at"]/1000,tz=tz.gettz('Australia/Brisbane'))

    position_quality = "Unknown"
    if a_position_info == 0:
        position_quality = "Simulated"
    elif a_position_info == 1:
        position_quality = "GPS Float"
    elif a_position_info == 2:
        position_quality = "RTK Fixed"
    elif a_position_info == 3:
        position_quality = "mm Enhanced"
    
    a_file_ptr.write("\n-, {}, {}, {}, {}, {}, -, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(device_id, machine_name, utc_time, position_quality, a_auto_grade_control, a_reverse, delay_id, operator_id, task_id, a_blade_left.getA1()[0], a_blade_left.getA1()[1], a_blade_left.getA1()[2], a_blade_right.getA1()[0], a_blade_right.getA1()[1], a_blade_right.getA1()[2]))


for line in response.iter_lines():
    decoded_line = base64.b64decode(line).decode('UTF-8')
    logging.debug(decoded_line)
    decoded_json = json.loads(decoded_line)

    if decoded_json['type'] == "sitelink::State":
        logging.debug("Found state.")

        if not decoded_json['data']['ac_uuid'] in state:
            state[decoded_json['data']['ac_uuid']] = {}

        if not decoded_json['data']['ns'] in state[decoded_json['data']['ac_uuid']]:
            state[decoded_json['data']['ac_uuid']][decoded_json['data']['ns']] = {}

        nested_state = { 
            "state" : decoded_json['data']['state'],
            "value" : decoded_json['data']['value']
        }
        state[decoded_json['data']['ac_uuid']][decoded_json['data']['ns']][decoded_json['data']['state']] = nested_state

        logging.debug("Current state: {}".format(json.dumps(state, indent=4)))

    if decoded_json['type'] == "mfk::Replicate":
        logging.debug("Found replicate.")
        rc_uuid = decoded_json['data']['rc_uuid']
        if not rc_uuid in resources:
            logging.debug("Getting RC_UUID (Resource Configuration).")
            resrouce_url = "{}/dba/v1/sites/{}/resources/{}".format(server_https.to_url(), args.site_id, rc_uuid)
            rc_uuid_response = session.get(resrouce_url, headers=headers)
            resources[rc_uuid] = rc_uuid_response.json()
            sdk_rc = resources[rc_uuid]
            sdk_rc["data"] = { "components": resources[rc_uuid]["components"] }
            sdk_rc.pop("components")
            logging.debug("Resource Configuration: {}".format(json.dumps(sdk_rc,indent=4)))
            rc = ResourceConfiguration(sdk_rc)
        else:
            logging.debug("Already have Resource Configuration for RC_UUID {}".format(rc_uuid))
        
        ac_uuid = decoded_json['data']['ac_uuid']
        if not ac_uuid in assets:
            logging.debug("Getting AC_UUID (Asset Context).")
            resrouce_url = "{}/dba/v1/sites/{}/resources/{}".format(server_https.to_url(), args.site_id, ac_uuid)
            ac_uuid_response = session.get(resrouce_url, headers=headers)
            assets[ac_uuid] = ac_uuid_response.json()
        else:
            logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))
        
        manifest = rc.apply_manifest(decoded_json['data']['manifest'])

        component = manifest.components[0]
        aux_control_data = component.interfaces["aux_control_data"].control_data

        res = next((sub for sub in aux_control_data if sub.id == "auto_grade_control"), None)
        auto_grade_control = res.value
        
        res = next((sub for sub in aux_control_data if sub.id == "reverse"), None)
        reverse = res.value

        res = next((sub for sub in aux_control_data if sub.id == "position_info"), None)
        position_info = res.value
        
        blade_l_local_space = GetPointOfInterestLocalSpace(a_component=component, a_point_of_interest="blade_l")
        blade_r_local_space = GetPointOfInterestLocalSpace(a_component=component, a_point_of_interest="blade_r")

        OutputLineItem(report_file, decoded_json, position_info, auto_grade_control, reverse, blade_l_local_space, blade_r_local_space, state[ac_uuid] if ac_uuid in state else {})
