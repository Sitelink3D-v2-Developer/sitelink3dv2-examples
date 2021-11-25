#!/usr/bin/python
import argparse
import datetime
import json
import logging
import os
import requests
import sys
import re

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "tokens"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "utils"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "reports"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "reports", "report_create"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "components", "reports", "report_download"))

from get_token      import *
from utils          import *
from report_traits  import *
from report_create  import *
from report_convert import *
from args           import *
from report_download import *

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

logger = logging.getLogger("create_and_download_haul_report_gpx_trails")

start_unix_time_millis = datetime_to_unix_time_millis(report_start_datetime)
end_unix_time_millis   = datetime_to_unix_time_millis(report_end_datetime)

report_name = args.name or "run {}".format(datetime.datetime.utcnow().replace(microsecond=0).isoformat())

# create haul report spanning the configured time range
haul_report_traits = HaulReportTraits(a_haul_states=["CYCLED"], a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis, a_results_header=headers)

report_job_id = create_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Haul {}".format(report_name), a_report_traits=haul_report_traits, a_report_term=args.term, a_headers=headers)
logging.info("Submitted [{}] called [{}] with job identifier [{}]".format(haul_report_traits.report_type(), report_name, report_job_id))
poll_job(a_server_config=server, a_site_id=args.site_id, a_term=args.term, a_job_id=report_job_id, a_headers=headers)

url = "{}/reporting/v1/{}/{}/{}".format(server.to_url(), args.site_id, "longterms", report_job_id)
result = json_from(requests.get(url, headers=headers))

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, args.site_id[0:12])

if "hauls" in result["results"] and "json" in result["results"]["hauls"]:
    download_url = result["results"]["hauls"]["json"] 
    report_name_base = re.sub(r'[^0-9_-a-zA-z]', '_', result["params"]["name"])
    report_name = report_name_base + "." + "hauls" + "." + "json"
    output_dir = os.path.join(current_dir, args.site_id[0:12], report_name_base)
    download_report(a_report_url=download_url, a_headers=haul_report_traits.results_header(), a_target_dir=output_dir, a_report_name=report_name) 

if "hauls" in result["results"] and "jsonl" in result["results"]["trails"]:
    download_url = result["results"]["trails"]["jsonl"] 
    report_name_base = re.sub(r'[^0-9_-a-zA-z]', '_', result["params"]["name"])
    report_name = report_name_base + "." + "trails" + "." + "jsonl"
    output_dir = os.path.join(current_dir, args.site_id[0:12], report_name_base)
    download_report(a_report_url=download_url, a_headers=haul_report_traits.results_header(), a_target_dir=output_dir, a_report_name=report_name) 

# extract the trails into individual files named according to the haul uuid for the trail
trail_json_dir = os.path.join(output_dir, "trails_json")
if not os.path.exists(trail_json_dir):
    os.makedirs(trail_json_dir, exist_ok=True)

trail_gpx_dir = os.path.join(output_dir, "trails_gpx")
if not os.path.exists(trail_gpx_dir):
    os.makedirs(trail_gpx_dir, exist_ok=True)

trail_gpx_trackpoints_dir = os.path.join(trail_gpx_dir, "trackpoints")
if not os.path.exists(trail_gpx_trackpoints_dir):
    os.makedirs(trail_gpx_trackpoints_dir, exist_ok=True)

trail_gpx_waypoints_dir = os.path.join(trail_gpx_dir, "waypoints")
if not os.path.exists(trail_gpx_waypoints_dir):
    os.makedirs(trail_gpx_waypoints_dir, exist_ok=True)

trail_file_name = os.path.join(output_dir, report_name_base + "." + "trails" + "." + "jsonl")

trails_json = {}

trails_json["source_report"] = report_name

with open(trail_file_name) as trail_file:
    for line in trail_file:
        trail=json.loads(line)
        trail_uuid = trail["uuid"]
        trail_file_json_name = os.path.join(trail_json_dir, trail_uuid + "." + "json")
        print (trail_file_json_name)
        with open(trail_file_json_name, "w") as outfile:
            outfile.write(json.dumps(trail, indent=4))
        
        trails_json[trail_uuid] = trail

        trail_file_trackpoint_gpx_name = os.path.join(trail_gpx_trackpoints_dir, trail_uuid + "." + "gpx")
        print (trail_file_trackpoint_gpx_name)        
        json_to_gpx_trackpoints(a_json_file_name=trail_file_json_name, a_gpx_file_name=trail_file_trackpoint_gpx_name)

        trail_file_waypoint_gpx_name = os.path.join(trail_gpx_waypoints_dir, trail_uuid + "." + "gpx")
        print (trail_file_waypoint_gpx_name)        
        json_to_gpx_waypoints(a_json_file_name=trail_file_json_name, a_gpx_file_name=trail_file_waypoint_gpx_name)

with open("converted.json", "w") as outfile:
    outfile.write(json.dumps(trails_json, indent=4))
    