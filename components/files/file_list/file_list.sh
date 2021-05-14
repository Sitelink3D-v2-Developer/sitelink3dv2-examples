#!/bin/bash
# Shell file to list files

## Settings for the site:
env="qa"
dc="us"
site_id=""

page_limit="100"
# start id uuid
start=""

## Authentication
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_list.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --start "$start" \
    --page_limit "$page_limit" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"