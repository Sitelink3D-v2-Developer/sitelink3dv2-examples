#!/bin/bash
## Batch file to list the sites at an organization / owner.

## Settings for the environment.
env="qa"
dc="us"

## Settings specific to this script.
# run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console to obtain the owner / organization identifier.
owner_id=""

## Authorization
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python site_list.py \
    --env "$env" \
    --dc "$dc" \
    --owner_id "$owner_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    