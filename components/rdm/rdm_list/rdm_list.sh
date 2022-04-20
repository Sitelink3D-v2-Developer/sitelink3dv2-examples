#!/bin/bash
## Shell file to list all RDM views and all data provided by those views at all domains at a sitelink site

## Settings for the environment.
env="qa"
dc="us"
site_id=""

page_limit="200"
start=""

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python rdm_list.py \
    --env "$env" \	
    --dc "$dc" \
    --site_id "$site_id" \
    --start "$start" \
    --page_limit "$page_limit" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
