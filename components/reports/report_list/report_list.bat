@echo off
rem ## Batch file to list the reports at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## optionally sort the results. sort_field may be either "job_type", "issued_at", "status" or "job_type".
rem # sorted results are ascending by default. ordering can be specified with sort_order="+" for ascending or sort_order="-" for descending. 
set sort_field="issued_at"
set sort_order="+"

rem ## Settings specific to this script.
set page_limit="500"
rem ## uuid
set start=""

rem ## optionally filter results. 
rem # to filter completed haul reports with names containing "day" issued since start of 2021 by anyone called smith:
rem set filter_issued_since_epoch="1609423200000"
rem set filter_job_type="rpt::haul_report"
rem set filter_name="*day*"
rem set filter_issued_by="*smith*"
rem set filter_status="complete"

set filter_issued_since_epoch=""
set filter_job_type=""
set filter_name=""
set filter_issued_by=""
set filter_status=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python report_list.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --sort_field %sort_field% ^
    --sort_order %sort_order% ^
    --page_limit %page_limit% ^
    --start %start% ^
    --filter_issued_since_epoch %filter_issued_since_epoch% ^
    --filter_job_type %filter_job_type% ^
    --filter_name %filter_name% ^
    --filter_issued_by %filter_issued_by% ^
    --filter_status %filter_status% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
