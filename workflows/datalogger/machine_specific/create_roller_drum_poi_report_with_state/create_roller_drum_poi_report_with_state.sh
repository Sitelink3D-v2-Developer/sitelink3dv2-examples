#!/bin/bash
## Shell file to read position and state information specific to rollers via the datalogger microservice. The output is written to a user specified CSV file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

# original roller activity window in ms from epoch
startms="1646187249000"
endms="1646187849394"

report_file_name="RollerReport.csv"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_roller_drum_poi_report_with_state.py \
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
    