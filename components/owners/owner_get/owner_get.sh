#!/bin/bash
## Shell file to list the specified organization / owner details.

## Settings for the environment.
env="qa"
dc="us"

## Settings specific to this script.
# The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
site_owner_uuid=""

## Authorization
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python owner_get.py \
    --env "$env" \
    --dc "$dc" \
    --site_owner_uuid "$site_owner_uuid" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"  
