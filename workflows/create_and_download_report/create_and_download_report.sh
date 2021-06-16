#!/bin/bash
# Shell file to run a number of reports, track their status and download the results as files.

## Settings for the site
env="qa"
dc="us"
site_id=""

## Authentication
oauth_id=""
oauth_secret=""
oauth_scope=""

## Settings for the reports:
report_iso_date_time_start="2020-12-31 09:21:00"
report_iso_date_time_end="2021-11-30 17:21:00"

exec python create_and_download_report.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" \
    --report_iso_date_time_start "$report_iso_date_time_start" \
    --report_iso_date_time_end "$report_iso_date_time_end" \
    --name "Linux Reporting"