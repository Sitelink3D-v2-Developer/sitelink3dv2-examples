#!/usr/bin/python
import json
import logging
import requests
import sys
import os
import urllib
import datetime
from dateutil import tz
import websocket
import ssl
import io

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "site_detail", "datalogger_utils", "transform", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

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

# the types of RDM data that are provided to us in UUID form that we can then use to lookup names for
state_name_lookup_list = ["operator", "delay", "id"] # id is task

def UpdateStateForAssetContext(a_state_msg, a_state_dict, a_server, a_site_id, a_headers):
    if not a_state_msg['data']['ac_uuid'] in a_state_dict:
        a_state_dict[a_state_msg['data']['ac_uuid']] = {}

    if not a_state_msg['data']['ns'] in a_state_dict[a_state_msg['data']['ac_uuid']]:
        a_state_dict[a_state_msg['data']['ac_uuid']][a_state_msg['data']['ns']] = {}

    nested_state = {
        "state" : a_state_msg['data']['state'],
        "value" : a_state_msg['data']['value']
    }

    # For certain states that provide UUID values, we want to also fetch the name for readability
    #if nested_state["state"] in state_name_lookup_list:
    page_traits = RdmViewPaginationTraits(a_page_size="500", a_start=[nested_state["value"]], a_end=[nested_state["value"], None])
    rj = query_rdm_by_domain_view(a_server_config=a_server, a_site_id=a_site_id, a_domain="sitelink", a_view="_head", a_headers=a_headers, a_params=page_traits.params())
    if len(rj["items"]) > 0: # There should be only one entry as we specified a unique ID
        object_name = "Unknown"
        if "operator" == nested_state["state"]:
            object_name = rj["items"][0]["value"]["firstName"] + " " + rj["items"][0]["value"]["lastName"]
        
        elif "delay" == nested_state["state"] or "id" == nested_state["state"]:
            object_name = rj["items"][0]["value"]["name"] 

        nested_state["name"] = object_name

    a_state_dict[a_state_msg['data']['ac_uuid']][a_state_msg['data']['ns']][a_state_msg['data']['state']] = nested_state

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

def FindComponentWithInterfaceInResourceConfiguration(a_resource_configuration, a_interface_name):
    for comp in a_resource_configuration.components:
        try:
            iface = comp.interfaces[a_interface_name]
            return comp
        except KeyError:
            pass
    return None

def SerialiseObjectList(a_object_list, a_header_list):

    # Dynamically build the output_string as a function of the available columns we've been given to write.
    output_string = ""

    # Output the columns by iterating over the header list. When we find the headers representing
    # the object name we're writing, we inject thd data. If we don't find the header names, we add them to
    # the list. They'll then be in the header list the next time we encounter data for that field.
    for obj in a_object_list:
        for item in obj["items"]:
            object_name = item["title"].replace(",","_")
            try:
                object_name_header_index = a_header_list.index(object_name)
            except ValueError:
                # add to list
                a_header_list.append(object_name)
                object_name_header_index = a_header_list.index(object_name)

    # Here we populate the value list at the index that matches the item title for this value in the header list, 
    # or None otherwise to correctly space the value list.
    value_list = [None for _ in range(len(a_header_list))]
    for obj in a_object_list:
        for item in obj["items"]:
            object_name = item["title"].replace(",","_")
            object_name_header_index = a_header_list.index(object_name)
            value_list[object_name_header_index] = "{}, ".format(item["value"])

    for val in value_list:
        val = "-, " if val is None else val
        output_string += val    
    
    return output_string

def FormatState(a_state):
    return a_state["name"] + " (" + a_state["value"] + ")"

# Write a variable list of "objects" each of which has a variable list of "items" to a serialised string that can be output to the CSV.
# The items will each have a "title" property that identifies the CSV header (effectively the column) that the data is to be associated
# with and written to. An example of an object may be a point of interest on the left of a machine blade or bucket. That point of interest
# will then have items representing the x, y and z coordinate for that point of interest with a title of a form similar to "blade left [x]",
# "blade left [y]" and "blade left [z]". This function would hence produce 3 outputs for that object before moving to the next. This approach
# allows objects to be defined outside of this object with no knowledge required of the structure of what's being serialised. For
# example another object may represent a single point in space represented by a WGS84 coordinate. That object's item list then may contain
# 3 items called "lat", "lon" and "height". Objects with shorter or longer item lists are also possible making this function flexible.
# The algorithm uses the title_list to manage where in the CSV output string each item is written so that data aligns with the comma
# separated titles when they're eventually written to file. State is written in a similar way but at fixed (known) column offsets.
#
def OutputLineObjects(a_file_ptr, a_machine_type, a_replicate, a_assets_dict, aux_control_data_dict, a_object_list, a_header_list, a_state={}):
    ac_uuid = a_replicate["data"]["ac_uuid"]
    machine_name = "-"
    device_id = "-"
    operator = "-"
    task = "-"
    delay = "-"
    surface_name = "-"

    try:
        operator = FormatState(a_state=a_state["topcon.rdm.list"]["operator"])
    except KeyError:
        logging.debug("No Operator state found.")

    try:
        delay = FormatState(a_state=a_state["topcon.rdm.list"]["delay"])
    except KeyError:
        logging.debug("No Delay state found.")

    try:
        task = FormatState(a_state=a_state["topcon.task"]["id"])
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

    position_string = SerialiseObjectList(a_object_list, a_header_list)

    machine_name_strip = machine_name.replace(",","_")
    delay_strip = delay.replace(",","_")
    operator_strip = operator.replace(",","_")
    task_strip = task.replace(",","_")
    surface_name_strip = surface_name.replace(",","_")

    a_file_ptr.write("\n{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(a_machine_type, device_id, machine_name_strip, utc_time, position_quality, position_error_horz, position_error_vert, auto_grade_control, reverse, delay_strip, operator_strip, task_strip, surface_name_strip, position_string))


def ProcessReplicate(a_decoded_json, a_resource_config_dict, a_assets_dict, a_state_dict, a_resources_dir, a_report_file, a_header_list, a_geodetic_header_list, a_transform_list, a_geodetic_coordinate_manager, a_line_index, a_server, a_site_id, a_headers, a_machine_description_filter=None):
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
        aux_control_data_comp = FindComponentWithInterfaceInResourceConfiguration(a_resource_configuration=resource_config_processor, a_interface_name="aux_control_data")
        aux_control_data_dict = GetAuxControlDataFromComponent(a_component=aux_control_data_comp)

        # Here we need to find the component(s) in the resource configuration that contains the points_of_interest interface.
        # This will contain the machine specific locations on the machine such as "front_drum_l" or "bucket_r" that we will
        # receive position updates for in replicate messages for logging. A machine may specify multiple components in its
        # resource configuration and any number of them may specify a points of interest interface so the following function
        # returns a list of all components reporting points of interest. Some machines such as haul truck don't specify any.
        # so the component_point_list may be legitimately empty.
        component_point_list = FindPointsOfInterestInResourceConfiguration(a_resource_configuration=resource_config_processor)
        # The component specifying the "transform" component is required to apply replicate manifest updates.
        transform_component = FindComponentWithInterfaceInResourceConfiguration(a_resource_configuration=resource_config_processor, a_interface_name="transform")

        asbuilt_shapes_comp = FindComponentWithInterfaceInResourceConfiguration(a_resource_configuration=resource_config_processor, a_interface_name="asbuilt_shapes")

        # Here we build our list of objects to print, each of which contains a list of items. This object list is passed to the
        # OutputLineObjects function to serialise for output. This object list is populated by a combination of two categories.
        # One of either:
        # 1. point of interest
        # 2. WGS 84 location
        # This is because 3DMC clients will report their positions in terms of (usually multiple) site localised points of
        # interest whereas haul truck clients report their positions in terms of a single postition in lat, lon,
        # height and direction.
        object_list = []
        geodetic_object_list = []
        local_position_added = False

        if asbuilt_shapes_comp is not None:

            asbuilt_shapes:mfk.AsBuiltShapes = asbuilt_shapes_comp.interfaces["asbuilt_shapes"]
            asbuilt_shapes.cache(asbuilt_shapes_comp)
            for shp in asbuilt_shapes.shapes:
                for vert in shp.vertices:
                    obj = {
                        "items" : []
                    }
                    node_name, prop = vert.point_reference.rsplit(".", 1)
                    for con in vert.constants:
                    
                        key, value_id = con.value_reference.rsplit(".", 1)
                        raw_sensors = asbuilt_shapes_comp.get_interface_object(key)
                        
                        if con.function == "dsty":
                            item = {
                                "title" : prop + "_density ({})".format(raw_sensors["description"]),
                                "value" : con.value
                            }
                            obj["items"].append(item)

                        if con.function == "vibf":
                            item = {
                                "title" : prop + "_vibration_freq ({})".format(raw_sensors["description"]),
                                "value" : con.value
                            }
                            obj["items"].append(item)

                        if con.function == "viba":
                            item = {
                                "title" : prop + " vibration_amp ({})".format(raw_sensors["description"]),
                                "value" : con.value
                            }
                            obj["items"].append(item)

                        if con.function == "spdm":
                            item = {
                                "title" : prop + "_speed ({})".format(raw_sensors["description"]),
                                "value" : con.value
                            }
                            obj["items"].append(item)

                        if con.function == "temp":
                            item = {
                                "title" : prop + "_temp ({})".format(raw_sensors["description"]),
                                "value" : con.value
                            }
                            obj["items"].append(item)

                    object_list.append(obj)

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

                # As an additional benefit, we also search the Transform interface for a local_position entry. This provides a single point
                # representation for the machine and is what's used in the Sitelink3D v2 web site machine list and for the machine icon pin
                # on the map. If available, we extract this local position and then convert it to WGS84 using the transform in use on site
                # at the time this replicate was produced.
                transform_interface = transform_component.interfaces["transform"]

                point = {
                    "z": transform_interface.local_position["elevation"],
                    "e": transform_interface.local_position["easting"],
                    "n": transform_interface.local_position["northing"]
                }


                item_z = {
                    "title" : "local_position [z]",
                    "value" : transform_interface.local_position["elevation"]
                }

                item_e = {
                    "title" : "local_position [e]",
                    "value" : transform_interface.local_position["easting"]
                }

                item_n = {
                    "title" : "local_position [n]",
                    "value" : transform_interface.local_position["northing"]
                }

                obj = {
                    "items" : [item_z,item_e,item_n]
                }

                object_list.append(obj)

                # We now use our transform list to find the transform that was in place at the time this replicate was produced.
                # Subsequently we'll convert to WGS84 using that approximation matrix.
                transform_info = get_transform_info_for_time(a_ms_since_epoch=a_decoded_json["at"], a_transform_list=a_transform_list)

                # Record the transform information for output to file
                object_list.append({
                        "items": [
                            {
                                "title": "Transform",
                                "value": "revision {} (file {})".format(transform_info["revision"], transform_info["file_name"])
                            }
                        ]  })

                # For efficiency we cache all local points and run WGS84 transformations on them all at the end of data processing. Otherwise
                # the need to lookup an approximation matrices for every replicate would make execution very slow.
                if not local_position_added:
                    # If we have good position quality, we add this local position to be transformed to WGS84. If not, we skip it and add a placeholder
                    # as attempting to transform bad positions may subsequently fail the request for a transformation matrix which aborts entire processing.
                    if "position_quality" in aux_control_data_dict.keys():
                        pos_quality = aux_control_data_dict["position_quality"] 
                        if pos_quality == 2 or pos_quality == 3: # "RTK Fixed" or "mm Enhanced"
                            if(math.isclose(point["e"], 0.0, abs_tol=0.00003) and math.isclose(point["n"], 0.0, abs_tol=0.00003)):
                                a_geodetic_coordinate_manager.skip_local_point("[unavailable - point at origin]")
                            else:
                                a_geodetic_coordinate_manager.add_local_point(point, transform_info)
                        elif pos_quality == 1:
                            a_geodetic_coordinate_manager.skip_local_point("[unavailable - low position quality]")
                        else:
                            a_geodetic_coordinate_manager.skip_local_point("[unavailable - position quality unknown]")
                    else:
                        a_geodetic_coordinate_manager.skip_local_point("[unavailable - position quality unknown]") # Initial Volvo app doesn't report position_quality and initial aftermarket excavator only reports 0 (Unknown)

                    local_position_added = True

        else:
            # This is likely a haul truck, but could be any client that simply wants to report WGS 84 positions rather
            # that site localised points. Look whether we can output lat,lon,alt,dir from the replicate.
            wgs_point = FindWgs84InResourceConfiguration(resource_config_processor, transform_component)
            if bool(wgs_point):
                obj = wgs84_coord_to_object_list_item(a_wgs_point=wgs_point)
                geodetic_object_list.append(obj)
                a_geodetic_coordinate_manager.add_geodetic_point(obj)

        OutputLineObjects(a_report_file, resource_config_processor._json["description"], a_decoded_json, a_assets_dict, aux_control_data_dict, object_list, a_header_list, a_state_dict[ac_uuid] if ac_uuid in a_state_dict else {})

def ProcessDataloggerToCsv(a_server, a_site_id, a_headers, a_target_dir, a_datalogger_start_ms, a_datalogger_end_ms, a_datalogger_output_file_name, a_machine_description_filter=None):

    # Before we fetch the raw data, we will first extract the history of localization at the site. This is required because any localized positions that we receive via
    # MFK replicate packets will be converted into WGS84 so that lat, lon and height information can also be output to the report making map plotting easy. As transforms
    # chage at the site the localized coordinates may also change so the WGS84 conversion must be performed using the site transform that was in use at the site at the
    # time the data was collected. For more information on the process of extracting localization history for a site see the workflow example called 
    # list_site_localization_history in this repository.
    localised, transform_revision = get_current_site_localisation(a_server=a_server, a_site_id=a_site_id, a_headers=a_headers)
    transform_list = []
    output_dir = make_site_output_dir(a_server_config=a_server, a_headers=a_headers, a_target_dir=a_target_dir, a_site_id=a_site_id)
    os.makedirs(output_dir, exist_ok=True)

    if localised:
        # Query and cache all versions of the localization history at this site.
        transform_list = query_and_download_site_localization_file_history(a_server_config=a_server, a_site_id=a_site_id, a_headers=a_headers, a_target_dir=output_dir)

    else:
        logging.info("Site not localized.")


    dba_url = "{}/dba/v1/sites/{}/updates?startms={}&endms={}&category=low_freq".format(a_server.to_url(), a_site_id, a_datalogger_start_ms, a_datalogger_end_ms)

    # get the datalogger data
    response = session.get(dba_url, headers=a_headers)
    response.raise_for_status()

    resource_definitions = {}
    assets = {}
    state = {}

    resources_dir = os.path.join(output_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)

    report_file_name_temp = os.path.join(output_dir, a_datalogger_output_file_name + ".tmp")
    report_file_temp = open(report_file_name_temp, "w")

    geodetic_file_name_temp = os.path.join(output_dir, a_datalogger_output_file_name + ".geo.tmp")
    geodetic_file_temp = open(geodetic_file_name_temp, "w")

    # We need to buffer the points of interest we receive from each component of each machine we encounter. This will be output
    # at the end of iteration over the full dataset so that the dynamic column titles can be fully identified over the entire dataset.

    point_of_interest_dict = {}

    geodetic_coordinate_manager = GeodeticCoordinateManager()

    # Main datalogger data processing loop
    header_list = []
    geodetic_header_list = []
    line_count = 0

    logging.info("Processing Data Logger output.")
    # record start of report execution to measure execution time
    start_time = time.time()

    for line in response.iter_lines():
        decoded_json = json.loads(base64.b64decode(line).decode('UTF-8'))

        if decoded_json['type'] == "sitelink::State":
            UpdateStateForAssetContext(a_state_msg=decoded_json, a_state_dict=state, a_server=a_server, a_site_id=a_site_id, a_headers=a_headers)
            logging.debug("Found state. Current state: {}".format(json.dumps(state, indent=4)))

        if decoded_json['type'] == "mfk::Replicate":
            try:
                ProcessReplicate(a_decoded_json=decoded_json, a_resource_config_dict=resource_definitions, a_assets_dict=assets, a_state_dict=state, a_resources_dir=resources_dir, a_report_file=report_file_temp, a_header_list=header_list, a_geodetic_header_list=geodetic_header_list, a_transform_list=transform_list ,a_geodetic_coordinate_manager=geodetic_coordinate_manager, a_line_index=line_count, a_server=a_server, a_site_id=a_site_id, a_headers=a_headers)
            except requests.exceptions.HTTPError:
                logging.warning("Could not process replicate.")
                continue
        line_count += 1

    logging.info("Writing report to {}".format(a_datalogger_output_file_name))

    report_file_temp.close()
    geodetic_file_temp.close()

    # batch process transform to wgs84 and to file
    geodetic_point_list = geodetic_coordinate_manager.calculate_geodetic_points(a_server=a_server, a_site_id=a_site_id, a_headers=a_headers)
    geodetic_file_temp = open(geodetic_file_name_temp, "w")
    for i, geodetic_point in enumerate(geodetic_point_list):
        geodetic_file_temp.write(SerialiseObjectList([geodetic_point], geodetic_header_list) + '\n')
    geodetic_file_temp.close()

    report_file_name = os.path.join(output_dir, a_datalogger_output_file_name)
    report_file = open(report_file_name, "w")
    column_count=13 # initial number of fixed columns as below
    report_file.write("Machine Type, Device ID, Machine Name, Time (UTC), GPS Mode, Error(H), Error(V), MC Mode, Reverse, Delay (ID), Operator (ID), Task (ID), Surface")
    for point_of_interest_name in header_list:
        report_file.write(", {}".format(point_of_interest_name))
        column_count += 1 # we use this to space out the geodetic columns later - each line has a variable number of columns from the temp file.

    for object_name in geodetic_header_list:
        report_file.write(", {}".format(object_name))
        
    first_line = True # The first line of the temp file is blank so we skip this
    geodetic_file_temp = open(geodetic_file_name_temp, "r")
    with open(report_file_name_temp, 'r') as report_file_temp:
        for line in report_file_temp:
            if first_line:
                first_line = False
                continue
            
            geo_line = geodetic_file_temp.readline()
            line_column_count = len(line.split(","))
            pad_string = " "
            line_diff = column_count - line_column_count
            
            while line_diff >= 0:
                pad_string += " -,"
                line_diff -= 1

            aggregate_line = "\n" + line.strip() + pad_string + geo_line.strip()[:-1]
            report_file.write(aggregate_line)

    report_file_temp.close()
    geodetic_file_temp.close()
    os.remove(report_file_name_temp)
    os.remove(geodetic_file_name_temp)

    end_time = time.time()

    elapsed_time = end_time - start_time

    logging.info("Processed {} lines in {} seconds".format(line_count + 1, elapsed_time)) # convert line_count from zero based indexing


class Asset():
    def __init__(self, asset_type, asset_class, a_oem=str(uuid.uuid4()), a_model=str(uuid.uuid4()), a_serial_number=str(uuid.uuid4()), a_asset_id=str(uuid.uuid4()), a_asset_uuid=str(uuid.uuid4())):
        self.asset_type = asset_type
        self.asset_class = asset_class
        self.oem = a_oem
        self.model = a_model
        self.serial_number = a_serial_number
        self.asset_id = a_asset_id
        self.asset_uuid = a_asset_uuid
        self.certificate, self.key_pair = generate_authorisation(self.asset_uuid, "sitelink@topcon.com")

    def get_urn(self):
        return "urn:X-topcon:{0}:ac:{1}:oem:{2}:model:{3}:sn:{4}:id:{5}".format(self.asset_type, self.asset_class, self.oem, self.model, self.serial_number, self.asset_id)

    def make_payload(self, at = None):
        certificate_pem = openssl.dump_certificate(openssl.FILETYPE_PEM, self.certificate)
        return {
            "type": "sitelink::Asset",
            "data": {
                "uuid": self.asset_uuid,
                "urn": self.get_urn(),
                "finger_print": self.certificate.digest("sha1").decode('utf-8'),
                "finger_print_algorithm": "SHA1",
                "public_id": {
                    "type":"RSA",
                    "public_pem_b64": base64.b64encode(certificate_pem).decode('utf-8'),
                }
            },
            "at": at or config.get_milliseconds_since_epoch(),
            "ttl": 57600,
        }

class AssetContext():
    def __init__(self, assets, lease_start = None):
        self.assets = assets
        self.uuid = str(uuid.uuid4())
        self.lease_start = lease_start or config.get_milliseconds_since_epoch()
        self.lease_ttl = 28800

    def make_payload(self):
        payload = {
            "uuid": self.uuid,
            "lease_start": self.lease_start,
            "lease_ttl": self.lease_ttl,
        }
        document = json.dumps(payload)
        document_b64 = base64.b64encode(document.encode('utf-8')).decode('utf-8')
        def get_asset_signature(asset):
            return {
                "algorithm": "SHA256-RSA",
                "asset_urn": asset.get_urn(),
                "asset_uuid": asset.asset_uuid,
                "signature_b64": base64.b64encode(openssl.sign(asset.key_pair, document, "sha256")).decode('utf-8'),
            }
        return {
            "type": "sitelink::AssetContext",
            "data": {
                "uuid": self.uuid,
                "lease_start": self.lease_start,
                "lease_ttl": self.lease_ttl,
                "signatures": [get_asset_signature(asset) for asset in self.assets],
                "document_b64": document_b64,
            },
            "at": self.lease_start,
            "ttl": self.lease_ttl,
        }

class DataLoggerAggregatorSocket():
    def __init__(self, a_server_config, a_site_id, a_dc, a_domain, a_region):
        self.site_id = a_site_id
        self.domain = a_domain
        self.region = a_region
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.ws.settimeout(2)
        dl_ws_url = "{}/data_logger/v1/publish_live/{}/{}/{}.{}".format(a_server_config.to_url(), a_dc, a_domain, a_site_id, a_region)
        self.ws.connect(dl_ws_url)
    def send(self, payload):
        return self.ws.send(payload)
    def receive(self):
        return self.ws.recv()
    def receive_ack(self):
        return map(int, self.ws.recv().split("\n"))
        
BEACON_LONG_TTL = 30000; # ms before low frequency beacon should be resent
BEACON_SHORT_TTL = 5000; # ms before high frequency beacon should be resent

def make_haul_mfk_replicate_payload(asset_context, rc_uuid, latitude, longitude, altitude, direction, at = None, beacon_expiry_epoch=0):
    manifest = io.BytesIO()
    manifest.write(struct.pack("<d", latitude))
    manifest.write(struct.pack("<d", longitude))
    manifest.write(struct.pack("<d", altitude))
    manifest.write(struct.pack("<f", direction))
    manifest.seek(0)

    at_payload = at or config.get_milliseconds_since_epoch()
    is_beacon = at_payload > beacon_expiry_epoch
    if is_beacon:
        beacon_expiry_epoch = at_payload + BEACON_LONG_TTL
  
    logging.info("BEACON IS {}, expiry is {}".format(is_beacon, beacon_expiry_epoch))
    return {
        "type": "mfk::Replicate",
        "data": {
            "ac_uuid": asset_context.uuid,
            "beacon": is_beacon,
            "local_bounds": {
                "type": "none",
            },
            "manifest": [
                base64.b64encode(manifest.read()).decode('utf-8'),
            ],
            "rc_uuid": rc_uuid,
        },
        "at": at_payload,
        "ttl": 30,
    }, beacon_expiry_epoch