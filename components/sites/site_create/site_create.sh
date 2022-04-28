#!/bin/bash
## Shell file to create a site.

## Settings for the environment.
env="qa"
dc="us"

## Site creation specifics.
# The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
site_owner_uuid="" 

site_name="API Site"
site_latitude=""
site_longitude=""
site_timezone=""

site_contact_name=""
site_contact_email=""
site_contact_phone=""

## Authorization.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python site_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_owner_uuid "$site_owner_uuid" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" \
    --site_name "$site_name" \
    --site_latitude "$site_latitude" \
    --site_longitude "$site_longitude" \
    --site_timezone "$site_timezone" \
    --site_contact_name "$site_contact_name" \
    --site_contact_email "$site_contact_email" \
    --site_contact_phone "$site_contact_phone"
  