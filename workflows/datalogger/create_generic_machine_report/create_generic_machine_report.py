#!/usr/bin/env python

import argparse
import requests
import logging
import json
import os
import sys
import base64
import urllib.parse

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "mfk"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "components", "datalogger"))

from get_token      import *
from utils          import *
from args           import *
from mfk            import *
from datalogger_payload import *
from datalogger_utils import *

# Configure Arguments
arg_parser = argparse.ArgumentParser(description="Read historical data from the datalogger microservice.")
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_logging(arg_parser, logging.INFO)
arg_parser = add_arguments_site(arg_parser)
arg_parser = add_arguments_auth(arg_parser)
arg_parser.add_argument("--startms", default="", help="Start of data ms since epoch", required=True)
arg_parser.add_argument("--endms", default="", help="End of data ms since epoch", required=True)

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

# get the datalogger data
response = session.get(dba_url, headers=headers)
response.raise_for_status()

resource_definitions = {}
assets = {}
mfk = {}

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, args.site_id[0:12])
os.makedirs(output_dir, exist_ok=True)

resources_dir = os.path.join(output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

state_file_name = os.path.join(output_dir, "states.txt")
event_file_name = os.path.join(output_dir, "events.txt")
kinematics_file_name = os.path.join(output_dir, "kinematics.txt")

payload_output_file = {}
payload_output_file["sitelink::Event"] = open(event_file_name, "w")
payload_output_file["sitelink::State"] = open(state_file_name, "w")
payload_output_file["mfk::Replicate"]  = open(kinematics_file_name, "w")


# Callback function to allow the payload processing code to lookup data it
# needs to log to file when format() is called. This callback means an MFK
# instance is not needed in the datalogger payload processing code.
# 
# The Replicate Interface within the cached Resource Configuration is used
# to determine the fields to query in the MFK interface. This provides the
# most recent data from the field for the provided UUID
def get_replicate_data_for_rc_uuid(a_rc_uuid):

    # Find the Topcon Replicate Interface definition within the Resource Configuration
    for rc_interface in resource_definitions[a_rc_uuid]["data"]["components"][0]["interfaces"]:
        if rc_interface["oem"] == "topcon" and rc_interface["name"] == "replicate":
            
            mfk_component = mfk[rc_uuid].components[0]
            vals = {}
            # The Topcon Replicate Interface manifest contains the field definitions appropriate 
            # for this RC UUID. These fields are used to query the associated data from the MFK code.
            # Fields are in the format <node.property> meaning that the following example in the
            # RC Interface results in a node of "topcon.transform.wgs" and property "lat".
            #
            # {
            #   "value_ref": "topcon.transform.wgs.lat",
            #   "type": "double"
            # }
            # 
            for val in rc_interface["manifest"]:
                node_name, prop = val["value_ref"].rsplit(".", 1)

                # We've found a node name so we can obtain the node of that name from the MFK code.
                node = mfk_component.get_interface_object(node_name)
                
                # Nodes are queried differently for the data they contain as a function of their
                # MFK type. This code handles the following types explicitly:
                # 1. <class 'mfk.AuxControlData.ControlData'>
                # 2. <class 'mfk.Nodes.Node'>
                if node:
                    if isinstance(node, Nodes.Node):
                        vals[val["value_ref"]] = getattr(node,prop)

                    elif isinstance(node, AuxControlData.ControlData):
                        vals[val["value_ref"]] = node.value
                    
                    else:
                        # start subscriptable data access
                        vals[val["value_ref"]] = node[prop]
                        # end subscriptable data access
                
            logging.debug("Returning values {} for RC UUID {}".format(vals, a_rc_uuid))
            return vals

# Extract the human readable machine name from the machine asset in the cached Asset Context definition.
def get_asset_name_for_ac_uuid(a_ac_uuid):
    machine_name = "Unknown"
    try:
        for i, val in enumerate(assets[ac_uuid]["signatures"]):
            if val["asset_urn"].startswith("urn:X-topcon:machine"):
                machine_name = urllib.parse.unquote(val["asset_urn"].split(":")[-1])
                break
    except KeyError as err:
        pass
    return machine_name

# Log formatted payload specific data to the provided file handle.
def LogPayload(a_payload, a_file):
    a_file.write("\n{}".format(a_payload.format()))

# Main datalogger data processing loop
line_count = 0
for line in response.iter_lines():
    line_count += 1
    decoded_json = json.loads(base64.b64decode(line).decode('UTF-8'))

    # Before we intepret the payload, we fetch the Asset Context and Resource Configuration
    # definitions and initialise the MFK code for the Resource Configuration if required. 
    #
    # This requires separate calls to the API so the results are cached to avoid the need to 
    # query on every message. 

    try:
        rc_uuid = decoded_json['data']['rc_uuid']
        if not rc_uuid in resource_definitions:

            logging.info("Getting Resource Configuration for RC_UUID {}".format(rc_uuid))
            resource_definitions[rc_uuid] = GetDbaResource(a_server_config=server_https, a_site_id=args.site_id, a_uuid=rc_uuid, a_headers=headers)

            mfk_rc = resource_definitions[rc_uuid]

            # The MFK code expects a slightly differnt JSON structure to that provided by DBA
            mfk_rc["data"] = { "components": resource_definitions[rc_uuid]["components"] }
            mfk_rc.pop("components")
            logging.debug("Resource Configuration: {}".format(json.dumps(mfk_rc,indent=4)))

            # Instantiate the MFK code for this Resource Configuration and cache it for subsequent queries.
            rc = ResourceConfiguration(mfk_rc)
            mfk[rc_uuid] = rc

            # Write the Resource Configuration to file for ease of inspection.
            resource_description = resource_definitions[rc_uuid]["description"] + " [" + resource_definitions[rc_uuid]["uuid"] + "]"
            resource_file_name = os.path.join(resources_dir, resource_description + ".json")
            resource_file = open(resource_file_name, "w")
            resource_file.write(json.dumps(resource_definitions[rc_uuid], indent=4))

        else:
            logging.debug("Already have Resource Configuration for RC_UUID {}".format(rc_uuid))
    
    except KeyError as err:
        pass    

    ac_uuid = decoded_json['data']['ac_uuid']
    if not ac_uuid in assets:
        logging.info("Getting Asset Context for AC_UUID {}".format(ac_uuid))
        assets[ac_uuid] = GetDbaResource(a_server_config=server_https, a_site_id=args.site_id, a_uuid=ac_uuid, a_headers=headers)

    else:
        logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))
      
    # Now that the Resource Configuration and Asset Context information is available we process each 
    # message before logging to file with the LogPayload function.
    # 
    # State and Event payloads are self contained and can be written to file without extra processing.
    # 
    # Replicate payloads however contain updates that must be applied to the MFK code instantiated for the
    # associated UUID. Once the replicate manifest is applied to the MFK code, the latter can be queried 
    # by the LogPayload function for the latest kinematic information which is then written to file. 

    payload = DataloggerPayload.payload_factory(decoded_json, get_asset_name_for_ac_uuid, get_replicate_data_for_rc_uuid)
    if payload is not None:
        logging.debug("Payload factory found {} {}".format(payload.payload_type(), payload.data_type()))
        logging.debug(payload.format())

        if payload.payload_type() == "mfk::Replicate":
            updated_manifest = mfk[rc_uuid].apply_manifest(payload.manifest())

        LogPayload(a_payload=payload, a_file=payload_output_file[payload.payload_type()])
    
logging.info("Processed {} lines".format(line_count))
