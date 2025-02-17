#!/usr/bin/python

# This example demonstrates how to produce a CSV output with a limilted summary based on a Sitelink3D weight report. 

import os
import sys
import openpyxl
import csv

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = os.path.join(path_up_to_last("workflows", False), "components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "site_detail", "get_token", "report_traits", "report_create", "report_download", "events"]:
    exec(import_cmd(components_dir, imp))

script_name = os.path.basename(os.path.realpath(__file__))

# >> Argument handling  
args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_site_id, arg_report_name, arg_datalogger_start_ms, arg_datalogger_end_ms, arg_datalogger_output_file_name, arg_datalogger_output_folder, arg_report_issued_by, arg_report_term, arg_data_update_method])
# << Argument handling

# >> Server & logging configuration
server = ServerConfig(a_environment=args.env, a_data_center=args.dc)
logging.basicConfig(format=args.log_format, level=int(args.log_level))
logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server.to_url(), args.dc, args.site_id))
# << Server & logging configuration

headers = headers_from_jwt_or_oauth(a_jwt=args.jwt, a_client_id=args.oauth_id, a_client_secret=args.oauth_secret, a_scope=args.oauth_scope, a_server_config=server)

logger = logging.getLogger("create_and_export_weight_summary_report")

target_dir = args.datalogger_output_folder
output_dir = make_site_output_dir(a_server_config=server, a_headers=headers, a_target_dir=target_dir, a_site_id=args.site_id)
       
report_job_monitor = report_job_monitor_factory(a_data_method=args.data_update_method, a_server_config=server, a_site_id=args.site_id, a_report_term=args.report_term, a_headers=headers)
report_job_monitor_callback = report_job_monitor.monitor_job

# recorde start of report execution to measure execution time
start_time = time.time()

# create reports spanning the configured time range
report_file_name="{}.xlsx".format(args.datalogger_output_file_name)
weight_report_traits = WeightReportTraits(a_results_header=headers, a_start_unix_time_millis=args.datalogger_start_ms, a_end_unix_time_millis=args.datalogger_end_ms)
create_and_download_report(a_server_config=server, a_site_id=args.site_id, a_report_name=args.report_name, a_report_traits=weight_report_traits, a_report_term=args.report_term, a_target_dir=output_dir, a_job_report_monitor_callback=report_job_monitor_callback, a_headers=headers, a_issued_by=args.report_issued_by, a_report_file_name=report_file_name)

end_time = time.time()

elapsed_time = end_time - start_time
logging.info("Execution time using data monitor method ({}): {} seconds.".format(args.data_update_method, elapsed_time))

xl_file = os.path.join(output_dir, report_file_name)

report_exists = True
try:
    wb_obj = openpyxl.load_workbook(xl_file)
except FileNotFoundError:
    logging.info("No Results.")  
    report_exists = False

if report_exists:
    wb_obj.active = wb_obj['Weights']
    sheet_obj = wb_obj.active

    # we retain columns (1 based) 1,2,6,7,9,12,25,30
    sheet_obj.delete_cols(31, 5)
    sheet_obj.delete_cols(26, 4)
    sheet_obj.delete_cols(13, 12)
    sheet_obj.delete_cols(10, 2)
    sheet_obj.delete_cols(8, 1)
    sheet_obj.delete_cols(3, 3)
 
csv_file = os.path.join(output_dir, args.datalogger_output_file_name) 
with open(csv_file, 'w', newline="") as f:
    if report_exists:
        c = csv.writer(f)
        for row in sheet_obj.iter_rows(values_only=True):
            c.writerow(row)

        os.remove(os.path.join(output_dir,report_file_name))
