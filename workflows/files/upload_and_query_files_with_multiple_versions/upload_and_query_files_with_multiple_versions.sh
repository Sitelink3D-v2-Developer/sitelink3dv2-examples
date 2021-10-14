#!/bin/bash
## Shell script to upload multiple versions of a single file rather than multiple files of the same name.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

design_file_name="tps-bris.tp3"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python upload_and_query_files_with_multiple_versions.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --design_file_name "$design_file_name" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
