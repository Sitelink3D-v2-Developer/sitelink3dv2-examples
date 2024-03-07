#!/bin/bash
## Shell file to produce a CSV output with a limilted summary based on a Sitelink3D weight report.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

# original machine activity window in ms from epoch
# https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
datalogger_start_ms="1514728800000"
datalogger_end_ms="1710468615902"

datalogger_output_file_name="WeightSummaryExport.csv"
datalogger_output_folder="/temp/Excel"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

## Settings for the reports:
report_name="Weight_Summary_Export"
report_issued_by="Python Example"

## Specify whether report job status should be determined via polling or event handling. Options are "event" or "poll".
data_update_method="event"

exec python create_and_export_weight_summary_report.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" \
    --datalogger_start_ms "$datalogger_start_ms" \
    --datalogger_end_ms "$datalogger_end_ms" \
    --datalogger_output_file_name "$datalogger_output_file_name" \
    --datalogger_output_folder "$datalogger_output_folder" \
    --report_name "$report_name" \
    --report_issued_by "$report_issued_by" \
    --data_update_method "$data_update_method"
    