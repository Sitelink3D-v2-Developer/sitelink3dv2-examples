#!/bin/bash
## Shell file to download design data generated on machines as landxml files.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

page_limit="200"
start=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python monitor_device_design_data.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --page_limit "$page_limit" \
    --start "$start" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
