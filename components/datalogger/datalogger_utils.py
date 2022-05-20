#!/usr/bin/python
import json
import logging
import requests
import sys
import os
import urllib

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "mfk"))

from mfk import *
from datalogger_utils import *

session = requests.Session()

def GetDbaResource(a_server_config, a_site_id, a_uuid, a_headers):
    resrouce_url = "{}/dba/v1/sites/{}/resources/{}".format(a_server_config.to_url(), a_site_id, a_uuid)
    resource_response = session.get(resrouce_url, headers=a_headers)
    return resource_response.json()

# Extract the human readable machine name from the supplied machine asset.
def get_machine_name_for_ac_uuid(a_asset_contexts, a_ac_uuid):
    machine_name = "Unknown"
    try:
        for i, val in enumerate(a_asset_contexts[a_ac_uuid]["signatures"]):
            if val["asset_urn"].startswith("urn:X-topcon:machine"):
                machine_name = urllib.parse.unquote(val["asset_urn"].split(":")[-1])
                break
    except KeyError as err:
        pass
    return machine_name

# Callback function to allow the payload processing code to lookup data it
# needs to log to file when format() is called. This callback means an MFK
# instance is not needed in the datalogger payload processing code.
# 
# The Replicate Interface within the cached Resource Configuration is used
# to determine the fields to query in the MFK interface. This provides the
# most recent data from the field for the provided UUID
def get_replicate_data_for_interface(a_rc_interfaces, rc_uuid_mfk_component_instance):

    # Find the Topcon Replicate Interface definition within the Resource Configuration
    for rc_interface in a_rc_interfaces:
        if rc_interface["oem"] == "topcon" and rc_interface["name"] == "replicate":
            
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
                node = rc_uuid_mfk_component_instance.get_interface_object(node_name)
                
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
                
            return vals