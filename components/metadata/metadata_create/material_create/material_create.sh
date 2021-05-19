#!/bin/bash
# Shell script to create a new material at a Sitelink3D v2 site.

## Settings for the site
env="qa"
dc="us"
site_id=""

## Material specifics
material_name="API Material"

## Auth
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python material_create.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --material_name "$material_name" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"