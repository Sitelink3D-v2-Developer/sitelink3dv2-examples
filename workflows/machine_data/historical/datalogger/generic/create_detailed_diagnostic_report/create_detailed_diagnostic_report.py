#!/usr/bin/env python

# This example demonstrates the power of accessing historical raw data at a site using the Datalogger service. The Datalogger service provides
# historical data over a specified time period in a format consistent with the way data is provided live with MFK Live. That is to say that
# the data consists of three broad message types:
# 1. Events (not used in this example).
# 2. State.
# 3. MFK updates (Machine Forward Kinematics).
#
# This script is one of many potential applications for such raw data. Here, a detailed report of all (low frequency) machine positions along
# with associated state, position and AsBuilt related flags as well as RDM metadata such as selected Task and design information is produced.
# Interpreting raw Datalogger data enables API consumers to build their own customized reports or otherwise process data for statistical or
# any other purpose.
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

for imp in ["args", "utils", "get_token", "mfk", "site_detail", "datalogger_utils", "transform", "rdm_pagination_traits", "rdm_list"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_datalogger_start_ms, arg_datalogger_end_ms, arg_datalogger_output_file_name, arg_datalogger_output_folder])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc, a_scheme="https")
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)
# remove any previous error files in case one is generated from below exception handling
target_dir=args.datalogger_output_folder


output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=target_dir, a_site_id=args.site_id)
os.makedirs(output_dir, exist_ok=True)
error_file_name = os.path.join(output_dir, "error.txt")

try:
    os.remove(error_file_name)
    logging.info("Removed previous error file.")
except OSError as error:
    pass

try:
    ProcessDataloggerToCsv(a_server=server, a_site_id=args.site_id, a_headers=headers, a_target_dir=target_dir, a_datalogger_start_ms=args.datalogger_start_ms, a_datalogger_end_ms=args.datalogger_end_ms, a_datalogger_output_file_name=args.datalogger_output_file_name)
except SitelinkProcessingError as e:
    log_and_exit_on_error(a_message=e, a_target_dir=output_dir)    
