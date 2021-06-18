#!/bin/bash
## Shell script to create a new region at a Sitelink3D v2 site.

## Settings for the site:
env="qa"
dc="us"
site_id=""

## Region specifics
region_name="API Region from Linux"
region_verticies_file="verticies/brisbane.txt"

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python region_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --region_name "$region_name" \
    --region_verticies_file "$region_verticies_file" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
