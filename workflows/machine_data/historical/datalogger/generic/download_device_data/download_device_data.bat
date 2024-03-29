@echo off
rem ## Batch file to read device survey data from all machines at the specified site for the specified time range. The output is written to a user specified CSV file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem # original machine activity window in ms from epoch
rem # https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
set time_start_ms="1689084000000"
set time_end_ms="1689429600000"

set datalogger_output_file_name="DeviceData.csv"
set datalogger_output_folder="C:\\temp\\Excel"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python download_device_data.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --time_start_ms %time_start_ms% ^
    --time_end_ms %time_end_ms% ^
    --datalogger_output_file_name %datalogger_output_file_name% ^
    --datalogger_output_folder %datalogger_output_folder% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    