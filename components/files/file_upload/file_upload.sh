#!/bin/bash
# Shell file to upload file

## Settings for the site:
env="qa"
dc="us"
site_id=""

file_name=""
file_name="file_to_upload.txt"
file_uuid=""
parent_uuid=""

## Authentication
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_upload.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --file_name "$file_name" \
    --file_uuid "$file_uuid" \
    --parent_uuid "$parent_uuid" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"