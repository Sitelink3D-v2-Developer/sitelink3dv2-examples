#!/bin/bash
## Shell file to run a haul report, download the resulting trail data and convert each haul to gpx format for display in third party tools.

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

exec python create_and_download_haul_report_gpx_trails.py \
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
    --report_name "$report_name"
