#!/usr/bin/env python
import logging
import os
import sys
from textwrap import indent
from dateutil import tz
import urllib

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "site_detail", "datalogger_utils"]:
    exec(import_cmd(components_dir, imp))

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

# get the datalogger data
response = session.get(dba_url, headers=headers)
logging.debug(response.text)
response.raise_for_status()

resource_definitions = {}
assets = {}
state = {}

# get site name for output directory
site_name = site_detail(server_https, headers, args.site_id)["name"]

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, args.site_id[0:12] + " [" + site_name + "]")
os.makedirs(output_dir, exist_ok=True)

resources_dir = os.path.join(output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

report_file_name = os.path.join(output_dir, args.report_file_name)
report_file = open(report_file_name, "w")

# We need to buffer the points of interest we receive from each component of each machine we encounter. This will be output
# at the end of iteration over the full dataset so that the dynamic column titles can be fully identified over the entire dataset.

point_of_interest_dict = {}

# Write a variable list of "objects" each of which has a variable list of "items" to a serialised string that can be output to the CSV.
# The items will each have a "title" property that identifies the CSV header (effectively the column) that the data is to be associated
# with and written to. An example of an object may be a point of interest on the left of a machine blade or bucket. That point of interest
# will then have items # representing the x, y and z coordinate for that point of interest with a title of a form similar to "blade left [x]",
# "blade left [y]" and "blade left [z]". This function would hence produce 3 outputs for that object before moving to the next. This approach
# allows objects to be defined outside of this object with no knowledge requried of the structure of what's being serialised. For
# example another object may represent a single point in space represented by a WGS84 coordinate. That object's item list then may contain
# 3 items called "lat", "lon" and "height". Objects with shorter or longer item lists are also possible making this function flexible.
# The algorithm uses the title_list to managed where in the CSV output string each item is written so that data aligns with the comma
# separated titles when they're eventually written to file. State is written in a similar way but at fixed (known) column offsets.
#
def OutputLineObjects(a_file_ptr, a_machine_type, a_replicate, aux_control_data_dict, a_object_list, a_header_list, a_state={}):
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

    for i, val in enumerate(assets[ac_uuid]["signatures"]):
        if val["asset_urn"].startswith("urn:X-topcon:machine"):
            machine_name = urllib.parse.unquote(val["asset_urn"].split(":")[-1])

        if val["asset_urn"].startswith("urn:X-topcon:device"):
            device_id = urllib.parse.unquote(val["asset_urn"].split(":")[-1])

    utc_time = datetime.datetime.fromtimestamp(a_replicate["at"]/1000,tz=tz.gettz('Australia/Brisbane'))

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

    # here we populate the value list at the index that matches the POI title for this value in the
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

    a_file_ptr.write("\n-, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(a_machine_type, device_id, machine_name, utc_time, position_quality, position_error_horz, position_error_vert, auto_grade_control, reverse, delay_id, operator_id, task_id, surface_name, position_string))

# Main datalogger data processing loop
header_list = []
line_count = 0
for line in response.iter_lines():
    line_count += 1
    decoded_json = json.loads(base64.b64decode(line).decode('UTF-8'))

    if decoded_json['type'] == "sitelink::State":
        logging.debug("Found state.")
        UpdateStateForAssetContext(a_state_msg=decoded_json, a_state_dict=state)
        logging.debug("Current state: {}".format(json.dumps(state, indent=4)))

    if decoded_json['type'] == "mfk::Replicate":
        logging.debug("Found replicate.")
        rc_uuid = decoded_json['data']['rc_uuid']
        rc_updated = UpdateResourceConfiguration(a_resource_config_uuid=rc_uuid, a_resource_config_dict=resource_definitions, a_server=server_https, a_site_id=args.site_id, a_headers=headers)
        if rc_updated:
            # Write the Resource Configuration to file for ease of inspection.
            resource_description = resource_definitions[rc_uuid]["description"] + " [" + resource_definitions[rc_uuid]["uuid"][0:8] + "]"
            resource_file_name = os.path.join(resources_dir, resource_description + ".json")
            resource_file = open(resource_file_name, "w")
            resource_file.write(json.dumps(resource_definitions[rc_uuid], indent=4))

        resource_config_processor = UpdateResourceConfigurationProcessor(a_resource_config_uuid=rc_uuid, a_resource_config_dict=resource_definitions)

        ac_uuid = decoded_json['data']['ac_uuid']
        if not ac_uuid in assets:
            logging.debug("Getting AC_UUID (Asset Context).")
            resrouce_url = "{}/dba/v1/sites/{}/resources/{}".format(server_https.to_url(), args.site_id, ac_uuid)
            ac_uuid_response = session.get(resrouce_url, headers=headers)
            assets[ac_uuid] = ac_uuid_response.json()
        else:
            logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))

        Replicate.load_manifests(resource_config_processor, decoded_json['data']['manifest'])

        # Here we need to find the component in the resource configuration that contains the aux_control_data interface.
        # This will contain position quality information if available for this machine. A machine may specify multiple
        # components in its resource configuration but only one of those components will specify aux control data.
        aux_control_data_comp = FindAuxControlDataComponentInResourceConfiguration(a_resource_configuration=resource_config_processor)
        aux_control_data_dict = GetAuxControlDataFromComponent(a_component=aux_control_data_comp)

        # Here we need to find the component in the resource configuration that contains the points_of_interest interface.
        # This will contain the machine specific locations on the machine such as "front_drum_l" or "bucket_r" that we will
        # receive position updates for in replicate messages for logging. A machine may specify multiple components in its
        # resource configuration and any number of them may specify a points of interest interface so the following function
        # returns a list of all components reporting points of interest. Some machines such as haul truck don't specify any.
        # so the component_point_list may be legitimately empty.
        component_point_list = FindPointsOfInterestInResourceConfiguration(a_resource_configuration=resource_config_processor)
        # The component specifying the "transform" component is required to apply replicate manifest updates.
        transform_component = FindTransformComponentInResourceConfiguration(a_resource_configuration=resource_config_processor)

        # Here we build our list of objects, each of which contains a list of items. This object list is passed to the
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

        OutputLineObjects(report_file, resource_config_processor._json["description"], decoded_json, aux_control_data_dict, object_list, header_list, state[ac_uuid] if ac_uuid in state else {})

logging.info("Writing report to {}".format(args.report_file_name))

report_file.close()

with open(report_file_name, 'r+') as report_file:
   content = report_file.read()
   report_file.seek(0)
   report_file.write("Machine ID, Machine Type, Device ID, Machine Name, Time (UTC), GPS Mode, Error(H), Error(V), MC Mode, Reverse, Delay Id, Operator Id, Task Id, Surface Name")
   for point_of_interest_name in header_list:
    if point_of_interest_name == "lat" or point_of_interest_name == "lon" or point_of_interest_name == "alt" or point_of_interest_name == "dir":
        report_file.write(", {}".format(point_of_interest_name))
    else:
        report_file.write(", {}".format(point_of_interest_name))

   report_file.write(content)

logging.info("Processed {} lines".format(line_count))
