#!/bin/bash
## Shell file to list the reports at a site. 

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## optionally sort the results. sort_field may be either "job_type", "issued_at", "status" or "job_type".
# sorted results are ascending by default. ordering can be specified with sort_order="+" for ascending or sort_order="-" for descending. 
sort_field="issued_at"
sort_order="+"

## Settings specific to this script.
page_limit="500"
## uuid
start=""

## optionally filter results. 
# to filter completed haul reports with names containing "day" issued since start of 2021 by anyone called smith:
# filter_issued_since_epoch="1609423200000"
# filter_job_type="rpt::haul_report"
# filter_name="*day*"
# filter_issued_by="*smith*"
# filter_status="complete"
filter_issued_since_epoch=""
filter_job_type=""
filter_name=""
filter_issued_by=""
filter_status=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python report_list.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --sort_field "$sort_field" \
    --sort_order "$sort_order" \
    --page_limit "$page_limit" \
    --start "$start" \
    --filter_issued_since_epoch "$filter_issued_since_epoch" \
    --filter_job_type "$filter_job_type" \
    --filter_name "$filter_name" \
    --filter_issued_by "$filter_issued_by" \
    --filter_status "$filter_status" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
    