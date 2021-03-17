#!/bin/bash
# Shell file to create a site.

## Settings for the site:
env="qa"
dc="us"
site_id=""

folder_name="Linux Folder"
folder_uuid=""
parent_uuid=""

## Authentication
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""


exec python folder_create.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --folder_name "$folder_name" \
    --folder_uuid "$folder_uuid" \
    --parent_uuid "$parent_uuid" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
