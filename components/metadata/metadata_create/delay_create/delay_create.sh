#!/bin/bash
## Shell script to create a new delay at a Sitelink3D v2 site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Delay specifics
delay_name="Traffic"
delay_code="D01"

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python delay_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --delay_name "$delay_name" \
    --delay_code "$delay_code" \
    --jwt "$jwt" \   
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
