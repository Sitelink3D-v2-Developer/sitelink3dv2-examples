#!/bin/bash
## Shell file to list the active and archived files and folders at a site. 

## ## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Settings specific to this script.
page_limit="100"
## uuid
start=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_list.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --start "$start" \
    --page_limit "$page_limit" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"