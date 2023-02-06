#!/usr/bin/python

# This example demonstrates how the data in a haul report can be used to create gpx files able to be
# loaded into and viewed with Google Maps or any compatible viewer. Doing so can provide additional 
# insights into haul data such as speed and elevation plots depending on the viewer software in use.
#
# The following is an overview of this example:
# 1. Create a new haul report covering the time period specified by report_iso_date_time_start and 
#    report_iso_date_time_end in the wrapper bat or sh file.
# 2. Download that haul report when it has completed. The report job is polled.
# 3. Create trackpoint and waypoint information in the local file system based on the report data.

import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "site_detail", "get_token", "report_traits", "report_create", "report_convert", "report_download"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_report_name, arg_report_term, arg_report_iso_date_time_start, arg_report_iso_date_time_end])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

report_start_datetime = parse_iso_date_to_datetime(args.report_iso_date_time_start)
report_end_datetime   = parse_iso_date_to_datetime(args.report_iso_date_time_end)
start_unix_time_millis = datetime_to_unix_time_millis(report_start_datetime)
end_unix_time_millis   = datetime_to_unix_time_millis(report_end_datetime)

report_name = args.report_name or "run {}".format(datetime.datetime.utcnow().replace(microsecond=0).isoformat())

# create haul report spanning the configured time range
converted_units= {
    "axis":"volume",
    "volume":"cubic_metres"
}
haul_report_traits = HaulReportTraits(a_haul_states=["CYCLED"], a_sub_type="cycles", a_converted_units=converted_units, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis, a_results_header=headers)

report_job_id = create_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Haul {}".format(report_name), a_report_traits=haul_report_traits, a_report_term=args.report_term, a_headers=headers)
logging.info("Submitted [{}] called [{}] with job identifier [{}]".format(haul_report_traits.report_type(), report_name, report_job_id))
poll_job(a_server_config=server, a_site_id=args.site_id, a_report_term=args.report_term, a_report_job_id=report_job_id, a_headers=headers)

url = "{}/reporting/v1/{}/{}/{}".format(server.to_url(), args.site_id, "longterms", report_job_id)
result = json_from(requests.get(url, headers=headers))

output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)

report_output_dir = ""
report_name_base = ""

if "hauls" in result["results"] and "json" in result["results"]["hauls"]:
    download_url = result["results"]["hauls"]["json"] 
    report_name_base = re.sub(r'[^0-9_-a-zA-z]', '_', result["params"]["name"])
    report_name = report_name_base + "." + "hauls" + "." + "json"
    report_output_dir = os.path.join(output_dir, report_name_base)
    download_report(a_report_url=download_url, a_headers=haul_report_traits.results_header(), a_target_dir=report_output_dir, a_report_name=report_name) 

if "hauls" in result["results"] and "jsonl" in result["results"]["trails"]:
    download_url = result["results"]["trails"]["jsonl"] 
    report_name_base = re.sub(r'[^0-9_-a-zA-z]', '_', result["params"]["name"])
    report_name = report_name_base + "." + "trails" + "." + "jsonl"
    report_output_dir = os.path.join(output_dir, report_name_base)
    download_report(a_report_url=download_url, a_headers=haul_report_traits.results_header(), a_target_dir=report_output_dir, a_report_name=report_name) 

# extract the trails into individual files named according to the haul uuid for the trail
trail_json_dir = os.path.join(report_output_dir, "trails_json")
if not os.path.exists(trail_json_dir):
    os.makedirs(trail_json_dir, exist_ok=True)

trail_gpx_dir = os.path.join(report_output_dir, "trails_gpx")
if not os.path.exists(trail_gpx_dir):
    os.makedirs(trail_gpx_dir, exist_ok=True)

trail_gpx_trackpoints_dir = os.path.join(trail_gpx_dir, "trackpoints")
if not os.path.exists(trail_gpx_trackpoints_dir):
    os.makedirs(trail_gpx_trackpoints_dir, exist_ok=True)

trail_gpx_waypoints_dir = os.path.join(trail_gpx_dir, "waypoints")
if not os.path.exists(trail_gpx_waypoints_dir):
    os.makedirs(trail_gpx_waypoints_dir, exist_ok=True)

trail_file_name = os.path.join(report_output_dir, report_name_base + "." + "trails" + "." + "jsonl")

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
    