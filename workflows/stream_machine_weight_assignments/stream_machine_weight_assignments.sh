#!/bin/bash
# Shell file to stream information about the weight assignment payload data sent from loading machines to haul trucks at a site.

## Settings for the site
env="qa"
dc="us"
site_id=""

## Authentication
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python stream_machine_weight_assignments.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 