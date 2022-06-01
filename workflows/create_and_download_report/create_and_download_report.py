#!/usr/bin/python
import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "report_traits", "report_create", "report_download"]:
    exec(import_cmd(components_dir, imp))

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

arg_parser.add_argument("--mask_region_uuid", default = "")
arg_parser.add_argument("--task_uuid", default = "")
arg_parser.add_argument("--sequence_instance", default = "")

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

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, args.site_id[0:12])
       
# create haul, delay, weight, activity & height map reports spanning the configured time range
haul_report_traits = HaulReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis, a_haul_states=["CYCLED"])
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Haul {}".format(report_range_name), a_report_traits=haul_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)

delay_report_traits = DelayReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Delay {}".format(report_range_name), a_report_traits=delay_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)

weight_report_traits = WeightReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Weight {}".format(report_range_name), a_report_traits=weight_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)

activity_report_traits = ActivityReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Activity {}".format(report_range_name), a_report_traits=activity_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)

tds_report_traits = TdsReportTraits(a_results_header=headers, a_server_config=server, a_site_id=args.site_id, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="TDS {}".format(report_range_name), a_report_traits=tds_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)

xyz_heigh_map_report_traits = XyzHeightMapReportTraits(a_server_config=server, a_site_id=args.site_id, a_date_unix_time_millis=end_unix_time_millis, a_mask_region_uuid=args.mask_region_uuid, a_task_uuid=args.task_uuid, a_seqence_instance=args.sequence_instance)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="XYZ Height Map {}".format(report_epoch_name), a_report_traits=xyz_heigh_map_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)

ply_heigh_map_report_traits = PlyHeightMapReportTraits(a_server_config=server, a_site_id=args.site_id, a_date_unix_time_millis=end_unix_time_millis, a_mask_region_uuid=args.mask_region_uuid, a_task_uuid=args.task_uuid, a_seqence_instance=args.sequence_instance)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="PLY Height Map {}".format(report_epoch_name), a_report_traits=ply_heigh_map_report_traits, a_report_term=args.term, a_target_dir=output_dir, a_headers=headers)
