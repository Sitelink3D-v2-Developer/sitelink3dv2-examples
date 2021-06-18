#!/bin/bash
# Shell file to stream information about the weight assignment payload data sent from loading machines to haul trucks at a site.

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

exec python stream_machine_weight_assignments.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
