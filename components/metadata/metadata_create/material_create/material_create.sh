#!/bin/bash
## Shell script to create a new material at a site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Material specifics
material_name="API Material"

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python material_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --material_name "$material_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
