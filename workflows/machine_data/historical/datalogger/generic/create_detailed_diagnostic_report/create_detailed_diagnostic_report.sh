#!/bin/bash
## Shell file to read position and state information for all machine types via the datalogger microservice. The output is written to a user specified CSV file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

# original machine activity window in ms from epoch
# https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
datalogger_start_ms="1617163200000"
datalogger_end_ms="1661293119118"

datalogger_output_file_name="DiagnosticReport.csv"
datalogger_output_folder="/temp/Excel"

# configure the report to produce basic or advanced output 
# "basic": machine name & type, date & time, GPS fix mode & errors values, active task, surface & sequence, local and WGS84 position
# "advanced": all of basic plus device ID, machine control mode (auto), reverse flag, identifiers for active settings above, site transform & all machine points of interest
output_verbosity="advanced"

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
    --log_level "$log_level" \
    --datalogger_start_ms "$datalogger_start_ms" \
    --datalogger_end_ms "$datalogger_end_ms" \
    --datalogger_output_file_name "$datalogger_output_file_name" \
    --datalogger_output_folder "$datalogger_output_folder" \
    --output_verbosity "$output_verbosity" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    