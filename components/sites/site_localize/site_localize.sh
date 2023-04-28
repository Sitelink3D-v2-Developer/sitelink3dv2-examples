#!/bin/bash
## Shell file to localize a site.

## Settings for the environment.
env="qa"
dc="us"

## Site localization specifics.
site_id="" 
file_id=""
file_rev=""

## Authorization.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python site_localize.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --file_id "$file_id" \
    --file_rev "$file_rev" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
  