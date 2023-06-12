#!/bin/bash
## Shell file to upload a file.

## ## Settings for the environment.
env="qa"
dc="us"
site_id=""

file_name="file_to_upload.txt"
file_parent_uuid=""

rdm_domain="file_system" 

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_upload.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --file_name "$file_name" \
    --file_parent_uuid "$file_parent_uuid" \
    --rdm_domain "$rdm_domain" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
