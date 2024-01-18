#!/bin/bash
## Shell file to read device survey data from all machines at the specified site for the specified time range. The output is written to a user specified CSV file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

# original machine activity window in ms from epoch
# https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
time_start_ms="1689084000000"
time_end_ms="1689429600000"

datalogger_output_file_name="DeviceData.csv"
datalogger_output_folder="/temp/Excel"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python download_device_data.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --time_start_ms "$time_start_ms" \
    --time_end_ms "$time_end_ms" \
    --datalogger_output_file_name "$datalogger_output_file_name" \
    --datalogger_output_folder "$datalogger_output_folder" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
    