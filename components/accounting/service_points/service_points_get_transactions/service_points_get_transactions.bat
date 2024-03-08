@echo off
rem ## Batch script to download a file.

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

set datalogger_output_file_name="Consumption_Report.csv"
set datalogger_output_folder="C:\\temp\\Bat\\Excel"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python service_points_get_transactions.py ^
    --log_level %log_level% ^
    --datalogger_output_file_name %datalogger_output_file_name% ^
    --datalogger_output_folder %datalogger_output_folder% 
    