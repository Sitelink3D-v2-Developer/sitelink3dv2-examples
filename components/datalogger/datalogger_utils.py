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

# Callback function to allow payload processing code to lookup data it
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
                # 1. <class 'mfk.AuxControlData.ControlDataValue'>
                # 2. <class 'mfk.AuxControlData.ControlDataPosition'>
                # 3. <class 'mfk.Nodes.Node'>
                if node:
                    if isinstance(node, Nodes.Node) or isinstance(node, AuxControlData.ControlDataPosition):
                        vals[val["value_ref"]] = getattr(node,prop)

                    elif isinstance(node, AuxControlData.ControlDataValue):
                        vals[val["value_ref"]] = node.value

                    else:
                        # start subscriptable data access
                        vals[val["value_ref"]] = node[prop]
                        # end subscriptable data access

            return vals

def GetPointOfInterestLocalSpace(a_point_of_interest_component, a_transform_component, a_point_of_interest):

    transform_interface = a_transform_component.interfaces["transform"]
    points_of_interest_interface = a_point_of_interest_component.interfaces["points_of_interest"]

    poi_local_space = "-"

    try:
        poi = next((sub for sub in points_of_interest_interface.points if sub.id == a_point_of_interest), None)
        logging.debug("Using Point {}".format(poi))
        node = a_point_of_interest_component.get_interface_object(poi.node_ref)
        logging.debug("Using Node {}".format(node))
        node_transform = node.get_local_transform()

        # We want to multiply the POI's referenced (and pre-transformed) node by the POI's offset.
        # For excavators this may be the bucket left and right, the drum for rollers, the blade for dozers etc.
        # When processing replicates they're applied to a transform in the node (referenced by the point of interest) that's already been local transformed because UpdateTransform was already called in the MFK code.
        poi_offset = poi.get_point()
        transformed_offset_point =  node_transform * poi_offset

        # Each time a replicate comes in, point.GetNode().GetTransform() is getting that pre-transformed node and then applying this offset from the point (which is the point of interest offset apart from its parent transform).
        # Remember that a point of interest has a parent node (node reference).
        # That puts the point of interest in the correct local space relative to the root.
        machine_to_local_transform = transform_interface.get_transform()

        # the transformed offset point is then multiplied by the machine to local transform to get the actual world space n,e,z
        poi_local_space = machine_to_local_transform * transformed_offset_point

    except KeyError:
        logging.debug("KeyError")

    logging.debug("POI in local space {}".format(poi_local_space))

    return poi_local_space

def UpdateStateForAssetContext(a_state_msg, a_state_dict):
    if not a_state_msg['data']['ac_uuid'] in a_state_dict:
        a_state_dict[a_state_msg['data']['ac_uuid']] = {}

    if not a_state_msg['data']['ns'] in a_state_dict[a_state_msg['data']['ac_uuid']]:
        a_state_dict[a_state_msg['data']['ac_uuid']][a_state_msg['data']['ns']] = {}

    nested_state = {
        "state" : a_state_msg['data']['state'],
        "value" : a_state_msg['data']['value']
    }
    a_state_dict[a_state_msg['data']['ac_uuid']][a_state_msg['data']['ns']][a_state_msg['data']['state']] = nested_state

    logging.debug("Current state: {}".format(json.dumps(a_state_dict, indent=4)))

def UpdateResourceConfiguration(a_resource_config_uuid, a_resource_config_dict, a_server, a_site_id, a_headers):

    resource_configuration_updated = False

    if not a_resource_config_uuid in a_resource_config_dict:
        logging.debug("Getting RC_UUID (Resource Configuration).")
        resrouce_url = "{}/dba/v1/sites/{}/resources/{}".format(a_server.to_url(), a_site_id, a_resource_config_uuid)
        rc_uuid_response = session.get(resrouce_url, headers=a_headers)
        a_resource_config_dict[a_resource_config_uuid] = rc_uuid_response.json()
        resource_configuration_updated = True

    return resource_configuration_updated

def UpdateResourceConfigurationProcessor(a_resource_config_uuid, a_resource_config_dict):
    mfk_rc = a_resource_config_dict[a_resource_config_uuid]
    mfk_rc["data"] = { "components": a_resource_config_dict[a_resource_config_uuid]["components"] }
    if not a_resource_config_uuid in a_resource_config_dict:
        mfk_rc.pop("components")
    logging.debug("Resource Configuration: {}".format(json.dumps(mfk_rc,indent=4)))
    resource_config_processor = ResourceConfiguration(mfk_rc)
    return resource_config_processor

def GetAuxControlDataFromComponent(a_component):
    ret = {}
    if a_component==None:
        return ret
    aux_control_data = a_component.interfaces["aux_control_data"].control_data

    result = next((sub for sub in aux_control_data if sub.id == "auto_grade_control"), None)
    ret["auto_grade_control"] = result.value

    result = next((sub for sub in aux_control_data if sub.id == "reverse"), None)
    ret["reverse"] = result.value

    result = next((sub for sub in aux_control_data if sub.id == "position_info"), None)
    ret["position_quality"] = result.quality
    ret["position_error_horz"] = result.error_horz
    ret["position_error_vert"] = result.error_vert

    return ret

def GetPointsOfInterestForResourceType(a_resource_description):

    if a_resource_description == "Generic Excavator (3DMC)":
        return {
            "transform_component" : "excavator basic",
            "points_component" : "excavator bucket",
            "points" : ["bucket_l", "bucket_r"]
        }
    elif a_resource_description == "Generic Bulldozer (3DMC)":
        return {
            "transform_component" : "Bulldozer with blade allowed full range of motion",
            "points_component" : "Bulldozer with blade allowed full range of motion",
            "points" : ["blade_l", "blade_r"]
        }
    elif a_resource_description == "Generic Asphalt Compactor (3DMC)":
        return {
            "transform_component" : "Asphalt compactor body and rollers",
            "points_component" : "Asphalt compactor body and rollers",
            "points" : ["front_drum_l", "front_drum_r"]
        }

    return None

def FindPointsOfInterestInResourceConfiguration(a_manifest):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    component_point_list = []

    for comp in a_manifest.components:

        points_of_interest = []

        try:
            iface = comp.interfaces["points_of_interest"]
        except KeyError:
            continue
        for point in iface._json["points"]:

            logging.debug("found POI: {}".format(point))
            point_of_interest = {
                "point_node" : point['id'],
                "display_name" : point['id']
            }
            if len(point["description"]) > 0:
                point_of_interest["display_name"] = point['id'] + " (" + point["description"] + ")"
            points_of_interest.append(point_of_interest)

        block = {
            "points_component" : comp,
            "points" : points_of_interest
        }
        component_point_list.append(block)

    return component_point_list

def FindWgs84InResourceConfiguration(a_manifest, a_transform_component):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    component_point_list = []
    transform_interface = a_transform_component.interfaces["transform"]

    for comp in a_manifest.components:
        try:
            iface = comp.interfaces["replicate"]
        except KeyError:
            continue
        this_wgs = {}
        man = iface._json["manifest"]

        for entry in man:
            base, ext = entry["value_ref"].rsplit(".", 1)
            if base == "topcon.transform.wgs":
                this_wgs[ext] = getattr(transform_interface.wgs, ext)

        logging.debug("extracted this wgs posision {}".format(json.dumps(this_wgs,indent=4)))

    return this_wgs

def FindTransformComponentInResourceConfiguration(a_manifest):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    for comp in a_manifest.components:
        try:
            iface = comp.interfaces["transform"]
            return comp
        except KeyError:
            pass
    return None

def FindAuxControlDataComponentInResourceConfiguration(a_manifest):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    for comp in a_manifest.components:
        try:
            iface = comp.interfaces["aux_control_data"]
            return comp
        except KeyError:
            pass
    return None
