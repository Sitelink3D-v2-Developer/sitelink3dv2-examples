@echo off
rem ## Batch file to run a haul report, download the resulting trail data and convert each haul to gpx format for display in third party tools.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

rem ## Settings for the reports:
set report_iso_date_time_start="2023-03-01 17:21:00"
set report_iso_date_time_end="2023-03-07 17:21:00"
set report_name=""

python create_and_download_haul_report_gpx_trails.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% ^
    --report_iso_date_time_start %report_iso_date_time_start% ^
    --report_iso_date_time_end %report_iso_date_time_end% ^
    --report_name %report_name%
    