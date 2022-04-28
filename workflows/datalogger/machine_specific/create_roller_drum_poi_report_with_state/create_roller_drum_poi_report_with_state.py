#!/usr/bin/env python

# This example demonstrates the power of accessing historical raw data at a site using the Datalogger service. The Datalogger service provides
# historical data over a specified time period in a format consistent with the way data is provided live with MFK Live. That is to say that
# the data consists of three broad message types:
# 1. Events (not used in this example).
# 2. State.
# 3. MFK updates (Machine Forward Kinematics).
#
# This script is one of many potential applications for such raw data. Here, a cut down version of the generic "create_detailed_diagnostic_report"
# example is provided specific to rollers. All (low frequency) machine positions along with associated state, position and AsBuilt related flags 
# as well as RDM metadata such as selected Task and design information is produced. Interpreting raw Datalogger data enables API consumers to build 
# their own customized reports or otherwise process data for statistical or any other purpose.
#
# The following is an overview of this example:
# 1. Extract raw data from the Datalogger (DBA) Service and iterate over the resulting lines.
# 2. Cache state information so that the most recent state is available to be output when kinematic updates are received.
# 3. Process mfk::Replicate packets containing binary encoded kinematic updates, conditioning the data to be output as a CSV line.


import logging
import os
import sys
from dateutil import tz
import urllib

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "mfk", "site_detail", "datalogger_utils"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_datalogger_start_ms, arg_datalogger_end_ms, arg_datalogger_output_file_name])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=args.log_level)
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

dba_url = "{}/dba/v1/sites/{}/updates?startms={}&endms={}&category=low_freq".format(server.to_url(), args.site_id, args.datalogger_start_ms, args.datalogger_end_ms)

# get the datalogger data
response = session.get(dba_url, headers=headers)
response.raise_for_status()

resource_definitions = {}
assets = {}
state = {}

output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
resources_dir = os.path.join(output_dir, "resources")
os.makedirs(resources_dir, exist_ok=True)

report_file_name_temp = os.path.join(output_dir, args.datalogger_output_file_name + ".tmp")
report_file_temp = open(report_file_name_temp, "w")

# We need to buffer the points of interest we receive from each component of each machine we encounter. This will be output
# at the end of iteration over the full dataset so that the dynamic column titles can be fully identified over the entire dataset.

point_of_interest_dict = {}

# Main datalogger data processing loop
header_list = []
line_count = 0
for line in response.iter_lines():
    line_count += 1
    decoded_json = json.loads(base64.b64decode(line).decode('UTF-8'))

    if decoded_json['type'] == "sitelink::State":
        UpdateStateForAssetContext(a_state_msg=decoded_json, a_state_dict=state)
        logging.debug("Found state. Current state: {}".format(json.dumps(state, indent=4)))

    if decoded_json['type'] == "mfk::Replicate":
        ProcessReplicate(a_decoded_json=decoded_json, a_resource_config_dict=resource_definitions, a_assets_dict=assets, a_state_dict=state, a_resources_dir=resources_dir, a_report_file=report_file_temp, a_header_list=header_list, a_server=server, a_site_id=args.site_id, a_headers=headers, a_machine_description_filter="Generic Asphalt Compactor (3DMC)")

logging.info("Writing report to {}".format(args.datalogger_output_file_name))

report_file_temp.close()

report_file_name = os.path.join(output_dir, args.datalogger_output_file_name)
report_file = open(report_file_name, "w")
report_file.write("Machine Type, Device ID, Machine Name, Time (UTC), GPS Mode, Error(H), Error(V), MC Mode, Reverse, Delay Id, Operator Id, Task Id, Surface Name")
for point_of_interest_name in header_list:
    report_file.write(", {}".format(point_of_interest_name))

with open(report_file_name_temp, 'r+') as report_file_temp:
    for line in report_file_temp:
        report_file.write(line)

report_file_temp.close()
os.remove(report_file_name_temp)

logging.info("Processed {} lines".format(line_count))
