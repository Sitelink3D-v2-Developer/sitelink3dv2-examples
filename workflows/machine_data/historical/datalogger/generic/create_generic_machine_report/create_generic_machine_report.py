#!/usr/bin/env python
import os
import sys

# This example demonstrates the power of accessing historical raw data at a site using the Datalogger service. The Datalogger service provides
# historical data over a specified time period in a format consistent with the way data is provided live with MFK Live. That is to say that
# the data consists of three broad message types:
# 1. Events.
# 2. State.
# 3. MFK updates (Machine Forward Kinematics).
#
# This script is one of many potential applications for such raw data. Here, the available events, state and kinematic updates are
# written to separate text files in human readable form to provide a generic overview of the activity at the site in a machine agnostic way.
# The detailed resource (machine definition) files for every asset encountered in the data stream over the specified time interval are written
# in a "resources" folder nested under the output folder.

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_payload", "datalogger_utils"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_datalogger_start_ms, arg_datalogger_end_ms])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=args.log_level)
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

logging.debug(headers)
dba_url = "{}/dba/v1/sites/{}/updates?startms={}&endms={}&category=low_freq".format(server.to_url(), args.site_id, args.datalogger_start_ms, args.datalogger_end_ms)
logging.debug("dba_url: {}".format(dba_url))

# get the datalogger data
response = session.get(dba_url, headers=headers)
response.raise_for_status()

resource_definitions = {}
assets = {}
mfk = {}

output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

resources_dir = os.path.join(output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

state_file_name = os.path.join(output_dir, "states.txt")
event_file_name = os.path.join(output_dir, "events.txt")
kinematics_file_name = os.path.join(output_dir, "kinematics.txt")

payload_output_file = {}
payload_output_file["sitelink::Event"] = open(event_file_name, "w")
payload_output_file["sitelink::State"] = open(state_file_name, "w")
payload_output_file["mfk::Replicate"]  = open(kinematics_file_name, "w")

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
    rc_uuid = ""
    rc_uuid_definition = None
    rc_uuid_mfk_component_instance = None
    try:    
        if decoded_json["type"] == "mfk::Replicate":
            rc_uuid = decoded_json['data']['rc_uuid']

            if not rc_uuid in resource_definitions:

                logging.debug("Getting Resource Configuration for RC_UUID {}".format(rc_uuid))
                resource_definitions[rc_uuid] = GetDbaResource(a_server_config=server, a_site_id=args.site_id, a_uuid=rc_uuid, a_headers=headers)

                mfk_rc = resource_definitions[rc_uuid]
                logging.debug("Resource Configuration: {}".format(json.dumps(mfk_rc,indent=4)))

                # Instantiate the MFK code for this Resource Configuration and cache it for subsequent queries.
                rc = ResourceConfiguration(mfk_rc)
                mfk[rc_uuid] = rc

                # Write the Resource Configuration to file for ease of inspection.
                resource_description = resource_definitions[rc_uuid]["description"] + " [" + resource_definitions[rc_uuid]["uuid"][0:8] + "]"
                resource_file_name = os.path.join(resources_dir, resource_description + ".json")
                resource_file = open(resource_file_name, "w")
                resource_file.write(json.dumps(resource_definitions[rc_uuid], indent=4))

            else:
                logging.debug("Already have Resource Configuration for RC_UUID {}".format(rc_uuid))

            rc_uuid_definition = resource_definitions[rc_uuid]["components"][0]["interfaces"]
            rc_uuid_mfk_component_instance = mfk[rc_uuid].components[0]
    except KeyError as err:
        logging.error("Error processing replicate resource configuration.")
        pass
    try:   
        ac_uuid = decoded_json['data']['ac_uuid']
        if not ac_uuid in assets:
            logging.debug("Getting Asset Context for AC_UUID {}".format(ac_uuid))
            assets[ac_uuid] = GetDbaResource(a_server_config=server, a_site_id=args.site_id, a_uuid=ac_uuid, a_headers=headers)

        else:
            logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))
    except KeyError as err:
        logging.error("Error processing replicate asset context.")
        pass

    # Now that the Resource Configuration and Asset Context information is available we process each
    # message before logging to file with the LogPayload function.
    #
    # State and Event payloads are self contained and can be written to file without extra processing.
    #
    # Replicate payloads however contain updates that must be applied to the MFK code instantiated for the
    # associated UUID. Once the replicate manifest is applied to the MFK code, the latter can be queried
    # by the LogPayload function for the latest kinematic information which is then written to file.
    try:
        payload = DataloggerPayload.payload_factory(decoded_json, assets, rc_uuid_definition, rc_uuid_mfk_component_instance)
        if payload is not None:
            logging.debug("Payload factory found {} {}".format(payload.payload_type(), payload.data_type()))
            logging.debug(payload.format())

            if payload.payload_type() == "mfk::Replicate":
                Replicate.load_manifests(mfk[rc_uuid], payload.manifest())
                mfk[rc_uuid].update_transforms()

            LogPayload(a_payload=payload, a_file=payload_output_file[payload.payload_type()])

    except KeyError as err:
        logging.error("Error processing replicate payload.")
        pass

logging.info("Processed {} lines".format(line_count))