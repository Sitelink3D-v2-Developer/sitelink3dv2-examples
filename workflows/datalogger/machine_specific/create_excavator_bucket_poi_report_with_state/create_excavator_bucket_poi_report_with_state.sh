#!/bin/bash
## Shell file to read position and state information specific to excavators via the datalogger microservice. The output is written to a user specified CSV file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

# original machine activity window in ms from epoch
startms="1651410000000"
endms="1659103200000"

report_file_name="ExcavatorReport.csv"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_excavator_bucket_poi_report_with_state.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --startms "$startms" \
    --endms "$endms" \
    --report_file_name "$report_file_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    