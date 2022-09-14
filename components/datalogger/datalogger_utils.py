#!/usr/bin/python
import json
import logging
import requests
import sys
import os
import urllib
import datetime
from dateutil import tz

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "mfk"))

from mfk import *
from datalogger_utils import *

session = requests.Session()

def GetDbaResource(a_server_config, a_site_id, a_uuid, a_headers):
    resource_url = "{}/dba/v1/sites/{}/resources/{}".format(a_server_config.to_url(), a_site_id, a_uuid)
    resource_response = session.get(resource_url, headers=a_headers)
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
                # <class 'mfk.Nodes.Node'>
                if node:
                    if isinstance(node, Nodes.Node):
                        vals[val["value_ref"]] = getattr(node,prop)
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
        transformed_offset_point =  poi_offset @ node_transform

        # Each time a replicate comes in, point.GetNode().GetTransform() is getting that pre-transformed node and then applying this offset from the point (which is the point of interest offset apart from its parent transform).
        # Remember that a point of interest has a parent node (node reference).
        # That puts the point of interest in the correct local space relative to the root.
        mfk_to_local_machine_update = Transform.J670ToLocal(1, True, 0, True, 2, True, True)
        machine_to_local_transform = transform_interface.get_transform(mfk_to_local_machine_update)

        # the transformed offset point is then multiplied by the machine to local transform to get the actual world space n,e,z
        poi_local_space = transformed_offset_point @ machine_to_local_transform

    except KeyError:
        logging.debug("KeyError")

    logging.debug("POI in local space {}".format(poi_local_space))

    return poi_local_space[0]

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
        resource_url = "{}/dba/v1/sites/{}/resources/{}".format(a_server.to_url(), a_site_id, a_resource_config_uuid)
        rc_uuid_response = session.get(resource_url, headers=a_headers)
        a_resource_config_dict[a_resource_config_uuid] = rc_uuid_response.json()
        resource_configuration_updated = True

    return resource_configuration_updated

def UpdateResourceConfigurationProcessor(a_resource_config_uuid, a_resource_config_dict):
    mfk_rc = a_resource_config_dict[a_resource_config_uuid]
    logging.debug("Resource Configuration: {}".format(json.dumps(mfk_rc,indent=4)))
    resource_config_processor = ResourceConfiguration(mfk_rc)
    return resource_config_processor

def GetAuxControlDataFromComponent(a_component):
    ret = {}
    if a_component==None:
        return ret
    aux_control_data = a_component.interfaces["aux_control_data"]
    ret["auto_grade_control"] = aux_control_data["auto_grade_control"]["value"]
    ret["reverse"] = aux_control_data["reverse"]["value"]
    ret["position_quality"] = aux_control_data["position_info"]["quality"]
    ret["position_error_horz"] = aux_control_data["position_info"]["error_horz"]
    ret["position_error_vert"] = aux_control_data["position_info"]["error_vert"]
    return ret

def FindPointsOfInterestInResourceConfiguration(a_resource_configuration):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    component_point_list = []

    for comp in a_resource_configuration.components:

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

def FindWgs84InResourceConfiguration(a_resource_configuration, a_transform_component):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    component_point_list = []
    transform_interface = a_transform_component.interfaces["transform"]

    for comp in a_resource_configuration.components:
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

def FindTransformComponentInResourceConfiguration(a_resource_configuration):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    for comp in a_resource_configuration.components:
        try:
            iface = comp.interfaces["transform"]
            return comp
        except KeyError:
            pass
    return None

def FindAuxControlDataComponentInResourceConfiguration(a_resource_configuration):
    # Iterate over the available components and find an interface with the description "points_of_interest"
    for comp in a_resource_configuration.components:
        try:
            iface = comp.interfaces["aux_control_data"]
            return comp
        except KeyError:
            pass
    return None

# Write a variable list of "objects" each of which has a variable list of "items" to a serialised string that can be output to the CSV.
# The items will each have a "title" property that identifies the CSV header (effectively the column) that the data is to be associated
# with and written to. An example of an object may be a point of interest on the left of a machine blade or bucket. That point of interest
# will then have items # representing the x, y and z coordinate for that point of interest with a title of a form similar to "blade left [x]",
# "blade left [y]" and "blade left [z]". This function would hence produce 3 outputs for that object before moving to the next. This approach
# allows objects to be defined outside of this object with no knowledge required of the structure of what's being serialised. For
# example another object may represent a single point in space represented by a WGS84 coordinate. That object's item list then may contain
# 3 items called "lat", "lon" and "height". Objects with shorter or longer item lists are also possible making this function flexible.
# The algorithm uses the title_list to managed where in the CSV output string each item is written so that data aligns with the comma
# separated titles when they're eventually written to file. State is written in a similar way but at fixed (known) column offsets.
#
def OutputLineObjects(a_file_ptr, a_machine_type, a_replicate, a_assets_dict, aux_control_data_dict, a_object_list, a_header_list, a_state={}):
    ac_uuid = a_replicate["data"]["ac_uuid"]
    machine_name = "-"
    device_id = "-"
    operator_id = "-"
    task_id = "-"
    delay_id = "-"
    surface_name = "-"

    try:
        operator_id = a_state["topcon.rdm.list"]["operator"]["value"]
    except KeyError:
        logging.debug("No Operator state found.")

    try:
        delay_id = a_state["topcon.rdm.list"]["delay"]["value"]
    except KeyError:
        logging.debug("No Delay state found.")

    try:
        task_id = a_state["topcon.task"]["id"]["value"]
    except KeyError:
        logging.debug("No Task state found.")

    try:
        surface_name = a_state["topcon.task"]["surface_name"]["value"]
    except KeyError:
        logging.debug("No Surface state found.")

    try:
        for i, val in enumerate(a_assets_dict[ac_uuid]["signatures"]):
            if val["asset_urn"].startswith("urn:X-topcon:machine"):
                machine_name = urllib.parse.unquote(val["asset_urn"].split(":")[-1])

            if val["asset_urn"].startswith("urn:X-topcon:device"):
                device_id = urllib.parse.unquote(val["asset_urn"].split(":")[-1])
    except KeyError:
        logging.debug("No machine or device information found.")

    utc_time = datetime.datetime.fromtimestamp(a_replicate["at"]/1000,tz=tz.UTC)

    position_quality = "Unknown"

    try:
        if aux_control_data_dict["position_quality"] == 0:
            position_quality = "Unknown"
        elif aux_control_data_dict["position_quality"] == 1:
            position_quality = "GPS Float"
        elif aux_control_data_dict["position_quality"] == 2:
            position_quality = "RTK Fixed"
        elif aux_control_data_dict["position_quality"] == 3:
            position_quality = "mm Enhanced"
    except:
        pass

    reverse = "Unknown"
    position_error_horz = "Unknown"
    position_error_vert = "Unknown"
    auto_grade_control = "Unknown"

    try:
        reverse = aux_control_data_dict["reverse"]
    except:
        pass
    try:
        position_error_horz = aux_control_data_dict["position_error_horz"]
    except:
        pass
    try:
        position_error_vert = aux_control_data_dict["position_error_vert"]
    except:
        pass
    try:
        auto_grade_control = aux_control_data_dict["auto_grade_control"]
    except:
        pass

    # Dynamically build the output position_string as a function of the available columns we've been given to write.
    position_string = ""

    # Output the position columns by iterating over the header list. when we find the headers representing
    # the point name we're writing, we inject thd data. If we don't find the header names, we add them to
    # the list and return. They'll then be in the header list the next time we encounter data for that field.
    for obj in a_object_list:
        for item in obj["items"]:
            point_name = item["title"]
            try:
                point_name_header_index = a_header_list.index(point_name)
            except ValueError:
                # add to list
                a_header_list.append(point_name)
                point_name_header_index = a_header_list.index(point_name)

    # Here we populate the value list at the index that matches the POI title for this value in the header list, or None otherwise to correctly space the value list for POIs.
    # header list, or None otherwise to correctly space the value list for POIs.
    value_list = [None for _ in range(len(a_header_list))]
    for obj in a_object_list:
        for item in obj["items"]:
            point_name = item["title"]
            point_name_header_index = a_header_list.index(point_name)
            value_list[point_name_header_index] = "{}, ".format(item["value"])

    for val in value_list:
        val = "-, " if val is None else val
        position_string += val

    a_file_ptr.write("\n{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(a_machine_type, device_id, machine_name, utc_time, position_quality, position_error_horz, position_error_vert, auto_grade_control, reverse, delay_id, operator_id, task_id, surface_name, position_string))

def ProcessReplicate(a_decoded_json, a_resource_config_dict, a_assets_dict, a_state_dict, a_resources_dir, a_report_file, a_header_list, a_server, a_site_id, a_headers, a_machine_description_filter=None):
        logging.debug("Found replicate.")
        rc_uuid = a_decoded_json['data']['rc_uuid']
        rc_updated = UpdateResourceConfiguration(a_resource_config_uuid=rc_uuid, a_resource_config_dict=a_resource_config_dict, a_server=a_server, a_site_id=a_site_id, a_headers=a_headers)
        resource_config_processor = UpdateResourceConfigurationProcessor(a_resource_config_uuid=rc_uuid, a_resource_config_dict=a_resource_config_dict)

        ac_uuid = a_decoded_json['data']['ac_uuid']
        if not ac_uuid in a_assets_dict:
            logging.debug("Getting AC_UUID (Asset Context).")
            resource_url = "{}/dba/v1/sites/{}/resources/{}".format(a_server.to_url(), a_site_id, ac_uuid)
            ac_uuid_response = session.get(resource_url, headers=a_headers)
            ac_uuid_response.raise_for_status()
            a_assets_dict[ac_uuid] = ac_uuid_response.json()
        else:
            logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))

        if a_machine_description_filter is not None:
            if a_machine_description_filter != resource_config_processor._json["description"]:
                return

        # Write the Resource Configuration to file for ease of inspection only if it passes the machine filter above.
        if rc_updated: 
            resource_description = a_resource_config_dict[rc_uuid]["description"] + " [" + a_resource_config_dict[rc_uuid]["uuid"][0:8] + "]"
            resource_file_name = os.path.join(a_resources_dir, resource_description + ".json")
            resource_file = open(resource_file_name, "w")
            resource_file.write(json.dumps(a_resource_config_dict[rc_uuid], indent=4))
        Replicate.load_manifests(resource_config_processor, a_decoded_json['data']['manifest'])
        resource_config_processor.update_transforms()

        # Here we need to find the component in the resource configuration that contains the aux_control_data interface.
        # This will contain position quality information if available for this machine. A machine may specify multiple
        # components in its resource configuration but only one of those components will specify aux control data.
        aux_control_data_comp = FindAuxControlDataComponentInResourceConfiguration(a_resource_configuration=resource_config_processor)
        aux_control_data_dict = GetAuxControlDataFromComponent(a_component=aux_control_data_comp)

        # Here we need to find the component(s) in the resource configuration that contains the points_of_interest interface.
        # This will contain the machine specific locations on the machine such as "front_drum_l" or "bucket_r" that we will
        # receive position updates for in replicate messages for logging. A machine may specify multiple components in its
        # resource configuration and any number of them may specify a points of interest interface so the following function
        # returns a list of all components reporting points of interest. Some machines such as haul truck don't specify any.
        # so the component_point_list may be legitimately empty.
        component_point_list = FindPointsOfInterestInResourceConfiguration(a_resource_configuration=resource_config_processor)
        # The component specifying the "transform" component is required to apply replicate manifest updates.
        transform_component = FindTransformComponentInResourceConfiguration(a_resource_configuration=resource_config_processor)

        # Here we build our list of objects to print, each of which contains a list of items. This object list is passed to the
        # OutputLineObjects function to serialise for output. This object list is populated by a combination of two categories.
        # One of either:
        # 1. point of interest
        # 2. WGS 84 location
        # This is because 3DMC clients will report their positions in terms of (usually multiple) site localised points of
        # interest whereas haul truck clients report their positions in terms of a single postition in lat, lon,
        # height and direction.
        object_list = []
        if len(component_point_list) > 0:

            for comp in component_point_list:

                for point in comp["points"]:

                    poi_local_space = GetPointOfInterestLocalSpace(a_point_of_interest_component=comp["points_component"], a_transform_component=transform_component, a_point_of_interest=point["point_node"])

                    item_x = {
                        "title" : point["display_name"] + " [x]",
                        "value" : poi_local_space[1]
                    }

                    item_y = {
                        "title" : point["display_name"] + " [y]",
                        "value" : poi_local_space[0]
                    }

                    item_z = {
                        "title" : point["display_name"] + " [z]",
                        "value" : poi_local_space[2]
                    }
                    obj = {
                        "items" : [item_x,item_y,item_z]
                    }

                    object_list.append(obj)
        else:
            # This is likely a haul truck, but could be any client that simply wants to report WGS 84 positions rather
            # that site localised points. Look whether we can output lat,lon,alt,dir from the replicate.
            wgs_point = FindWgs84InResourceConfiguration(resource_config_processor, transform_component)
            if bool(wgs_point):
                obj = {
                    "items" : []
                }
                try:
                    lat = wgs_point["lat"]
                    item_lat = {
                            "title" : "latitude",
                            "value" : lat
                        }
                    obj["items"].append(item_lat)
                except KeyError:
                    pass

                try:
                    lon = wgs_point["lon"]
                    item_lon = {
                            "title" : "longitude",
                            "value" : lon
                        }
                    obj["items"].append(item_lon)
                except KeyError:
                    pass

                try:
                    alt = wgs_point["alt"]
                    item_alt = {
                            "title" : "altitude",
                            "value" : alt
                        }
                    obj["items"].append(item_alt)
                except KeyError:
                    pass

                try:
                    dir = wgs_point["dir"]
                    item_dir = {
                            "title" : "direction",
                            "value" : dir
                        }
                    obj["items"].append(item_dir)
                except KeyError:
                    pass

                object_list.append(obj)

        OutputLineObjects(a_report_file, resource_config_processor._json["description"], a_decoded_json, a_assets_dict, aux_control_data_dict, object_list, a_header_list, a_state_dict[ac_uuid] if ac_uuid in a_state_dict else {})

