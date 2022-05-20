#!/bin/bash
## Shell file to determine the last know position for every machine appearing at the specified site for the last 24 hours using the datalogger microservice. The output is written in JSON format to a folder with the name of the site id.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python find_last_known_machine_positions.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    