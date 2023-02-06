#!/bin/bash
## Shell file to run a number of reports, track their status and download the results as files.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

## Settings for the reports:
report_iso_date_time_start="2020-12-31 09:21:00"
report_iso_date_time_end="2021-11-30 17:21:00"
report_name=""

## Specify whether report job status should be determined via polling or event handling. Options are "event" or "poll".
data_update_method="event"

## Optional settings specific to height map reports
report_mask_region_uuid=""
report_task_uuid=""
# sequence_instance if for level sequences: index formatted '%08d'; for shift sequences: 'YYYY-MM-DD`T`{startTime}' in site-local time
report_sequence_instance="" 

exec python create_and_download_report.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" \
    --report_iso_date_time_start "$report_iso_date_time_start" \
    --report_iso_date_time_end "$report_iso_date_time_end" \
    --report_mask_region_uuid "$report_mask_region_uuid" \
    --report_task_uuid "$report_task_uuid" \
    --report_sequence_instance "$report_sequence_instance" \
    --report_name "$report_name" \
    --data_update_method "$data_update_method"
