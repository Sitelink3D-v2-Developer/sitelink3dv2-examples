#!/bin/bash
# Shell file to stream information about the machines connected to a site.

## Settings for the site
env="qa"
dc="us"
site_id=""

## Authentication
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python stream_machines_on_site.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    