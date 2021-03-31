@echo off
rem # Batch file to run a number of reports, track their status and download the results as files.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Authentication
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

rem ## Settings for the reports:
set report_iso_date_time_start="2020-12-31 17:21:00"
set report_iso_date_time_end="2021-03-19 17:21:00"

python create_and_download_report.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% ^
    --report_iso_date_time_start %report_iso_date_time_start% ^
    --report_iso_date_time_end %report_iso_date_time_end% ^
    