#!/bin/bash
## Shell file to read position and state information for all machine types via the datalogger microservice. The output is written to a user specified CSV file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

# original machine activity window in ms from epoch
# https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
datalogger_start_ms="1617163200000"
datalogger_end_ms="1661293119118"

datalogger_output_file_name="DiagnosticReport.csv"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_detailed_diagnostic_report.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --datalogger_start_ms "$datalogger_start_ms" \
    --datalogger_end_ms "$datalogger_end_ms" \
    --datalogger_output_file_name "$datalogger_output_file_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    