#!/usr/bin/env python
import os
import sys
import json
from dateutil import tz

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_utils"]:
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

# get the data
response = session.get(dba_url, headers=headers)
logging.debug(response.text)
response.raise_for_status()

resources = {}
assets = {}
state = {}

logging.info("Writing report to {}".format(args.report_file_name))
report_file = open(args.report_file_name, "w")

report_file.write("Machine ID, Device ID, Machine Name, Time (UTC), GPS Mode, Error(H), Error(V), MC Mode, Speed (km/h), Reverse, Delay Id, Operator Id, Task Id, Left X, Left Y, Left Z, Right X, Right Y, Right Z")

def OutputLineItem(a_file_ptr, a_replicate, a_position_quality, a_position_error_horz, a_position_error_vert, a_auto_grade_control, a_reverse, a_blade_left, a_blade_right, a_state={}):
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
    if a_position_quality == 0:
        position_quality = "Unknown"
    elif a_position_quality == 1:
        position_quality = "GPS Float"
    elif a_position_quality == 2:
        position_quality = "RTK Fixed"
    elif a_position_quality == 3:
        position_quality = "mm Enhanced"

    a_file_ptr.write("\n-, {}, {}, {}, {}, {}, {}, {}, -, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(device_id, machine_name, utc_time, position_quality, a_position_error_horz, a_position_error_vert, a_auto_grade_control, a_reverse, delay_id, operator_id, task_id, a_blade_left[1], a_blade_left[0], a_blade_left[2], a_blade_right[1], a_blade_right[0], a_blade_right[2]))


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
            mfk_rc = resources[rc_uuid]
            mfk_rc["data"] = { "components": resources[rc_uuid]["components"] }
            mfk_rc.pop("components")
            logging.debug("Resource Configuration: {}".format(json.dumps(mfk_rc,indent=4)))
            rc = ResourceConfiguration(mfk_rc)
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

        Replicate.load_manifests(rc, decoded_json['data']['manifest'])

        component = rc.components[0]
        aux_control_data = component.interfaces["aux_control_data"]

        auto_grade_control = aux_control_data["auto_grade_control"]["value"]

        reverse = aux_control_data["reverse"]["value"]

        position_quality = aux_control_data["position_info"]["quality"]
        position_error_horz = aux_control_data["position_info"]["error_horz"]
        position_error_vert = aux_control_data["position_info"]["error_vert"]

        blade_l_local_space = GetPointOfInterestLocalSpace(a_point_of_interest_component=component, a_transform_component=component, a_point_of_interest="blade_l")
        blade_r_local_space = GetPointOfInterestLocalSpace(a_point_of_interest_component=component, a_transform_component=component, a_point_of_interest="blade_r")

        OutputLineItem(report_file, decoded_json, position_quality, position_error_horz, position_error_vert, auto_grade_control, reverse, blade_l_local_space, blade_r_local_space, state[ac_uuid] if ac_uuid in state else {})
