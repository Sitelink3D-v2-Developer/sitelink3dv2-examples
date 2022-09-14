#!/bin/bash
## Shell file to read generic machine position and state information via the datalogger microservice. The output is written to a folder with the name of the site id.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

# machine activity window in ms from epoch
# https://currentmillis.com/ is a convenient site to convert to and from "milliseconds since epoch".
datalogger_start_ms="1646961300000"
datalogger_end_ms="1646962619225"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_generic_machine_report.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --datalogger_start_ms "$datalogger_start_ms" \
    --datalogger_end_ms "$datalogger_end_ms" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    