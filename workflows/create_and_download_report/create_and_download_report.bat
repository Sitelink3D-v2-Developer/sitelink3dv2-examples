@echo off
rem ## Batch file to run a number of reports, track their status and download the results as files.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

rem ## Settings for the reports:
set report_iso_date_time_start="2020-12-31 17:21:00"
set report_iso_date_time_end="2021-11-09 17:21:00"
set report_name=""

rem ## Optional settings specific to height map reports
set report_mask_region_uuid=""
set report_task_uuid=""
rem # sequence_instance if for level sequences: index formatted '%08d'; for shift sequences: 'YYYY-MM-DD`T`{startTime}' in site-local time
set report_sequence_instance="" 

python create_and_download_report.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% ^
    --report_iso_date_time_start %report_iso_date_time_start% ^
    --report_iso_date_time_end %report_iso_date_time_end% ^
    --report_mask_region_uuid %report_mask_region_uuid% ^
    --report_task_uuid %report_task_uuid% ^
    --report_sequence_instance %report_sequence_instance% ^
    --report_name %report_name%
    