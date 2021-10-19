#!/bin/bash
## Shell file to stream information about the machines connected to a site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python stream_machines_on_site.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    