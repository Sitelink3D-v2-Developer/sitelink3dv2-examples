#!/bin/bash
## Shell file to query design data within a file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Settings specific to this script.
file_uuid=""
file_name=""

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_features.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --file_uuid "$file_uuid" \
    --file_name "$file_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
