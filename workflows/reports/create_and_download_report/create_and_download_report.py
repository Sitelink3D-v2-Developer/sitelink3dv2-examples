#!/usr/bin/python

# This example demonstrates how each of the report types available in Sitelink3D v2 is created. Reports 
# are created by using Traits classes that abstract away the details specific to the report types.
#
# The available report types are:
# 1. Haul
# 2. Delay
# 3. Weight
# 4. Activity
# 5. TDS
# 6. XYZ Height Map (AsBuilt)
# 7. PLY Height Map (AsBuilt)
#
# The following is an overview of this example:
# 1. Parse the arguments from the wrapper bat or sh file.
# 2. Create a traits object specific to each report type to be created and downloaded.
# 3. Create each report and monitor its progress via polling.
# 4. Download the results for each report once it has run.
#
# Note that an instructional video of this example is provided in the "videos" folder accompanying this example script.

import os
import sys

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "site_detail", "get_token", "report_traits", "report_create", "report_download", "events"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_log_level=logging.INFO, a_arg_list=[arg_site_id, arg_report_name, arg_report_term, arg_report_iso_date_time_start, arg_report_iso_date_time_end, arg_report_mask_region_uuid, arg_report_task_uuid, arg_report_sequence_instance, arg_data_update_method])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
logging.basicConfig(format=args.log_format, level=args.log_level)
logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

report_start_datetime = parse_iso_date_to_datetime(args.report_iso_date_time_start)
report_end_datetime   = parse_iso_date_to_datetime(args.report_iso_date_time_end)

logger = logging.getLogger("create_and_download_report")

start_unix_time_millis = datetime_to_unix_time_millis(report_start_datetime)
end_unix_time_millis   = datetime_to_unix_time_millis(report_end_datetime)

report_range_name = args.report_name or "Report for Period {} to {} run {}".format(report_start_datetime.isoformat(), report_end_datetime.isoformat(), datetime.datetime.utcnow().replace(microsecond=0).isoformat())
report_epoch_name = args.report_name or "Report for Epoch {} run {}".format(report_start_datetime.isoformat(), datetime.datetime.utcnow().replace(microsecond=0).isoformat())

output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_current_dir=os.path.dirname(os.path.realpath(__file__)), a_site_id=args.site_id)
       

report_job_monitor = report_job_monitor_factory(a_data_method=args.data_update_method, a_server_config=server, a_site_id=args.site_id, a_report_term=args.report_term, a_headers=headers)
report_job_monitor_callback = report_job_monitor.monitor_job

# recorde start of report execution to measure execution time
start_time = time.time()

# create reports spanning the configured time range
haul_report_traits = HaulReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis, a_haul_states=["CYCLED"], a_sub_type="cycles", a_converted_units={"axis":"volume","volume":"cubic_metres"})
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Haul {}".format(report_range_name), a_report_traits=haul_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

delay_report_traits = DelayReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Delay {}".format(report_range_name), a_report_traits=delay_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

weight_report_traits = WeightReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Weight {}".format(report_range_name), a_report_traits=weight_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

activity_report_traits = ActivityReportTraits(a_results_header=headers, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="Activity {}".format(report_range_name), a_report_traits=activity_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

tds_report_traits = TdsReportTraits(a_results_header=headers, a_server_config=server, a_site_id=args.site_id, a_start_unix_time_millis=start_unix_time_millis, a_end_unix_time_millis=end_unix_time_millis)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="TDS {}".format(report_range_name), a_report_traits=tds_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

xyz_heigh_map_report_traits = XyzHeightMapReportTraits(a_server_config=server, a_site_id=args.site_id, a_date_unix_time_millis=end_unix_time_millis, a_mask_region_uuid=args.report_mask_region_uuid, a_task_uuid=args.report_task_uuid, a_seqence_instance=args.report_sequence_instance)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="XYZ Height Map {}".format(report_epoch_name), a_report_traits=xyz_heigh_map_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

ply_heigh_map_report_traits = PlyHeightMapReportTraits(a_server_config=server, a_site_id=args.site_id, a_date_unix_time_millis=end_unix_time_millis, a_mask_region_uuid=args.report_mask_region_uuid, a_task_uuid=args.report_task_uuid, a_seqence_instance=args.report_sequence_instance)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name="PLY Height Map {}".format(report_epoch_name), a_report_traits=ply_heigh_map_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers)

end_time = time.time()

elapsed_time = end_time - start_time
logging.info("Execution time using data monitor method ({}): {} seconds.".format(args.data_update_method, elapsed_time))