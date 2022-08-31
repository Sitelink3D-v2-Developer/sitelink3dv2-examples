@echo off
rem ## Batch file to read position and state information specific to excavators via the datalogger microservice. The output is written to a user specified CSV file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem original machine activity window in ms from epoch
set datalogger_start_ms="1655410000000"
set datalogger_end_ms="1659103200000"

set datalogger_output_file_name="ExcavatorReport.csv"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_excavator_bucket_poi_report_with_state.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --datalogger_start_ms %datalogger_start_ms% ^
    --datalogger_end_ms %datalogger_end_ms% ^
    --datalogger_output_file_name %datalogger_output_file_name% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    