#!/bin/bash
## Shell file to upload file.

## ## Settings for the environment.
env="qa"
dc="us"
site_id=""

file_name="file_to_upload.txt"
file_uuid=""
parent_uuid=""

## There are two domains within which files are stored in Sitelink3D v2.
# use domain="file_system" to access general files that are visible on the "Site Files" tab in the File Manager.
# use domain="operator" to access topo data files from machines that are visible on the "Operator Files" tab in the File Manager.
# See the file_operator_upload.sh file for an example of uploading to the operator domain.
domain="file_system" 

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
    --file_uuid "$file_uuid" \
    --parent_uuid "$parent_uuid" \
    --domain "$domain" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
