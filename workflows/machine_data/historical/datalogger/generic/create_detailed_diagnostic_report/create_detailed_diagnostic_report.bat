@echo off
rem ## Batch file to read position and state information for all machine types via the datalogger microservice. The output is written to a user specified CSV file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem original machine activity window in ms from epoch
rem https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
set datalogger_start_ms="1661293109118"
set datalogger_end_ms="1661293119118"

set datalogger_output_file_name="DiagnosticReport.csv"
set datalogger_output_folder="C:\\temp\\Bat\\Excel"

rem configure the report to produce basic or advanced output 
rem "basic": machine name & type, date & time, GPS fix mode & errors values, active task, surface & sequence, local and WGS84 position
rem "advanced": all of basic plus device ID, machine control mode (auto), reverse flag, identifiers for active settings above, site transform & all machine points of interest
set output_verbosity="advanced"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_detailed_diagnostic_report.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --datalogger_start_ms %datalogger_start_ms% ^
    --datalogger_end_ms %datalogger_end_ms% ^
    --datalogger_output_file_name %datalogger_output_file_name% ^
    --datalogger_output_folder %datalogger_output_folder% ^
    --output_verbosity %output_verbosity% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    