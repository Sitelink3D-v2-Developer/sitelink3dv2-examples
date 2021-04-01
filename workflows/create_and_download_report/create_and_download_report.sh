#!/bin/bash
# Batch file to run a number of reports, track their status and download the results as files.

## Settings for the site
env="qa"
dc="us"
site_id="fdc59e465e0476fbf5bebc1314bf73c23b7ee0c1a095716b57a7440e1db4cd33"

## Authentication
oauth_id="2dc51e38-8b90-479d-a45a-6be25284e465"
oauth_secret="d481ab84-056c-454d-9615-f871a5f8558a"
oauth_scope="9f2337a2400adf146ff7629c0a391079"

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