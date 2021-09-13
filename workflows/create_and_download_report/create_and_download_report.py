#!/usr/bin/python
import argparse
import datetime
import json
import logging
import os
import requests
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "reports"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "reports", "report_create"))

from get_token      import *
from utils          import *
from report_traits  import *
from report_create  import *
from args           import *

# >> Arguments
arg_parser = argparse.ArgumentParser(description="Test reporting.")

# script parameters:
arg_parser = add_arguments_logging(arg_parser, logging.INFO)

# server parameters:
arg_parser = add_arguments_environment(arg_parser)
arg_parser = add_arguments_auth(arg_parser)
arg_parser.add_argument("--term", default="longterms")

# request parameters:
arg_parser.add_argument("--name", help="Name for the report")
arg_parser.add_argument("--report_iso_date_time_start", help="Start date for the report (in ISO date format)")
arg_parser.add_argument("--report_iso_date_time_end", help="End date for the report (in ISO date format)")

arg_parser.add_argument("--site_id", default="", help="Site Identifier")
arg_parser.set_defaults()
args = arg_parser.parse_args()
logging.basicConfig(format=args.log_format, level=args.log_level)
# << Arguments

# >> Server settings
session = requests.Session()

server = ServerConfig(a_environment=args.env, a_data_center=args.dc)

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)


logging.info("Running {0} for server={1} dc={2} site={3}".format(os.path.basename(os.path.realpath(__file__)), server.to_url(), args.dc, args.site_id))

# << Server settings

report_start_datetime = parse_iso_date_to_datetime(args.report_iso_date_time_start)
report_end_datetime   = parse_iso_date_to_datetime(args.report_iso_date_time_end)

logger = logging.getLogger("create_and_download_report")

start_unix_time_millis = datetime_to_unix_time_millis(report_start_datetime)
end_unix_time_millis   = datetime_to_unix_time_millis(report_end_datetime)

report_range_name = args.name or "Report for Period {} to {} run {}".format(report_start_datetime.isoformat(), report_end_datetime.isoformat(), datetime.datetime.utcnow().replace(microsecond=0).isoformat())
report_epoch_name = args.name or "Report for Epoch {} run {}".format(report_start_datetime.isoformat(), datetime.datetime.utcnow().replace(microsecond=0).isoformat())


       
# create haul, delay, weight, activity & height map reports spanning the configured time range
haul_report_traits = HaulReportTraits(a_report_subtype="hauls", a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis, a_results_header=headers)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Haul {}".format(report_range_name), a_report_traits=haul_report_traits, a_report_term=args.term, a_headers=headers)

delay_report_traits = DelayReportTraits(a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis, a_results_header=headers)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Delay {}".format(report_range_name), a_report_traits=delay_report_traits, a_report_term=args.term, a_headers=headers)

weight_report_traits = WeightReportTraits(a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Weight {}".format(report_range_name), a_report_traits=weight_report_traits, a_report_term=args.term, a_headers=headers)

activity_report_traits = ActivityReportTraits(a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Activity {}".format(report_range_name), a_report_traits=activity_report_traits, a_report_term=args.term, a_headers=headers)

xyz_heigh_map_report_traits = XyzHeightMapReportTraits(a_server_config=server, a_site_id=args.site_id, a_date_unix_time_millis=start_unix_time_millis) # additional requests required to access height map jobs
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="XYZ Height Map {}".format(report_epoch_name), a_report_traits=xyz_heigh_map_report_traits, a_report_term=args.term, a_headers=headers)

ply_heigh_map_report_traits = PlyHeightMapReportTraits(a_server_config=server, a_site_id=args.site_id, a_date_unix_time_millis=start_unix_time_millis) # additional requests required to access height map jobs
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="PLY Height Map {}".format(report_epoch_name), a_report_traits=ply_heigh_map_report_traits, a_report_term=args.term, a_headers=headers)
