@echo off
rem ## Batch file to produce a CSV output with a limilted summary based on a Sitelink3D weight report.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem # original machine activity window in ms from epoch
rem # https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
set datalogger_start_ms="1710467686519"
set datalogger_end_ms="1710467689519"

set datalogger_output_file_name="WeightSummaryExport.csv"
set datalogger_output_folder="C:\\temp\\Bat\\Excel"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

rem ## Settings for the reports:
set report_name="Weight_Summary_Export"
set report_issued_by="Python Example"

rem ## Specify whether report job status should be determined via polling or event handling. Options are "event" or "poll".
set data_update_method="event"

python create_and_export_weight_summary_report.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% ^
    --datalogger_start_ms %datalogger_start_ms% ^
    --datalogger_end_ms %datalogger_end_ms% ^
    --datalogger_output_file_name %datalogger_output_file_name% ^
    --datalogger_output_folder %datalogger_output_folder% ^
    --report_name %report_name% ^
    --report_issued_by %report_issued_by% ^
    --data_update_method %data_update_method%
    