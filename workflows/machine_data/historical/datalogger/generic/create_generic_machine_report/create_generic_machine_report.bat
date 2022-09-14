@echo off
rem ## Batch file to read generic machine position and state information via the datalogger microservice. The output is written to a folder with the name of the site id.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem machine activity window in ms from epoch
rem https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
set datalogger_start_ms="1646961300000"
set datalogger_end_ms="1646962619225"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_generic_machine_report.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --datalogger_start_ms %datalogger_start_ms% ^
    --datalogger_end_ms %datalogger_end_ms% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    