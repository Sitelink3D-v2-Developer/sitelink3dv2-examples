#!/bin/bash
## Shell file to create a folder.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

folder_name="Linux Folder"
folder_uuid=""
folder_parent_uuid=""

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python folder_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --folder_name "$folder_name" \
    --folder_uuid "$folder_uuid" \
    --folder_parent_uuid "$folder_parent_uuid" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
