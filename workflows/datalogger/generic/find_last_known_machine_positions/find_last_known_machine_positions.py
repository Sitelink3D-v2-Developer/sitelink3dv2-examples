#!/usr/bin/env python
import os
import sys
from textwrap import indent
import time

from numpy import sort

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "datalogger_payload", "datalogger_utils", "site_detail"]:
    exec(import_cmd(components_dir, imp))

# Configure Arguments
arg_parser = argparse.ArgumentParser(description="Read historical data from the datalogger microservice.")
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_logging(arg_parser, logging.INFO)
arg_parser = add_arguments_site(arg_parser)
arg_parser = add_arguments_auth(arg_parser)

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

endms = round(time.time() * 1000)
startms = endms - 86400000 # last 24 hours in ms

dba_url = "{}/dba/v1/sites/{}/updates?startms={}&endms={}&category=low_freq".format(server_https.to_url(), args.site_id, startms, endms)
logging.debug("dba_url: {}".format(dba_url))

# get the datalogger data
response = session.get(dba_url, headers=headers)
logging.debug(response.text)
response.raise_for_status()

resource_definitions = {}
assets = {}
mfk = {}

# get site name for output directory
site_name = site_detail(server_https, headers, args.site_id)["name"]

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, args.site_id[0:12] + " [" + site_name + "]")
os.makedirs(output_dir, exist_ok=True)

resources_dir = os.path.join(output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

positions_file_name = os.path.join(output_dir, "positions.json")
positions_file = open(positions_file_name, "w")
positions = {}

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
            resource_description = resource_definitions[rc_uuid]["description"] + " [" + resource_definitions[rc_uuid]["uuid"][0:8] + "]"
            resource_file_name = os.path.join(resources_dir, resource_description + ".json")
            resource_file = open(resource_file_name, "w")
            resource_file.write(json.dumps(resource_definitions[rc_uuid], indent=4))

        else:
            logging.debug("Already have Resource Configuration for RC_UUID {}".format(rc_uuid))

        ac_uuid = decoded_json['data']['ac_uuid']
        if not ac_uuid in assets:
            logging.info("Getting Asset Context for AC_UUID {}".format(ac_uuid))
            assets[ac_uuid] = GetDbaResource(a_server_config=server_https, a_site_id=args.site_id, a_uuid=ac_uuid, a_headers=headers)

        else:
            logging.debug("Already have Asset Context for AC_UUID {}".format(ac_uuid))

        # Now that the Resource Configuration and Asset Context information is available we process each
        # message before cachine machine position before logging to file.
        #
        # Replicate payloads contain updates that must be applied to the MFK code instantiated for the
        # associated UUID. Once the replicate manifest is applied to the MFK code, the latter can be queried
        # for the latest kinematic information which is then written to file.

        rc_uuid_definition = resource_definitions[rc_uuid]["data"]["components"][0]["interfaces"]
        rc_uuid_mfk_component_instance = mfk[rc_uuid].components[0]
        payload = DataloggerPayload.payload_factory(decoded_json, assets, rc_uuid_definition, rc_uuid_mfk_component_instance)
        if payload is not None:
            logging.debug("Payload factory found {} {}".format(payload.payload_type(), payload.data_type()))
            logging.debug(payload.format())

            if payload.payload_type() == "mfk::Replicate":
                Replicate.load_manifests(mfk[rc_uuid], payload.manifest())
                # log the position
                positions.update(payload.position())

    except KeyError as err:
        pass

positions_file.write(json.dumps(positions, indent=4))
logging.info("Processed {} lines".format(line_count))
