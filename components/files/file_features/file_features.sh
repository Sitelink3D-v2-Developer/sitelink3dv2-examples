#!/bin/bash
# Shell file to query design data within a file

## Settings for the site:
env="qa"
dc="us"
site_id=""

file_uuid=""
file_name=""

## Authentication
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_features.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --file_uuid "$file_uuid" \
    --file_name "$file_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"