#!/bin/bash
## Shell file to create a site ready to connect Topcon Haul App clients to.

## Settings for the site
env="qa"
dc="us"

## Site creation specifics
# run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console to obtain the owner / organization identifier.
owner_id=""

site_name="API Hauling Site"
site_latitude="-27.979320763437187" 
site_longitude="153.40316555667877"
site_timezone="Australia/Brisbane"

site_contact_name="Joe Burger"
site_contact_email="jb@jb.com"
site_contact_phone="123-456-7890"

site_auth_code="123123"

## Region specifics
region_discovery_file="regions/discovery_region_verticies.txt"
region_load_file="regions/load_region_verticies.txt"
region_dump_file="regions/dump_region_verticies.txt"

## Authorization.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_site_configured_for_hauling.py \
    --dc "$dc" \
    --env "$env" \
    --owner_id "$owner_id" \
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
    --site_contact_phone "$site_contact_phone" \
    --site_auth_code "$site_auth_code" \
    --region_discovery_verticies_file "$region_discovery_file" \
    --region_load_verticies_file "$region_load_file" \
    --region_dump_verticies_file "$region_dump_file" 
    