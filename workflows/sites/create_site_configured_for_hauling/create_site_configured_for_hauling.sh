#!/bin/bash
## Shell file to create a site ready to connect Topcon Haul App clients to.

## Settings for the site
env="qa"
dc="us"

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Site creation specifics
# The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
site_owner_uuid=""

site_name="API Hauling Site"
site_latitude="-27.979320763437187" 
site_longitude="153.40316555667877"
site_timezone="Australia/Brisbane"

site_contact_name="Joe Burger"
site_contact_email="jb@jb.com"
site_contact_phone="123-456-7890"

site_auth_code="123123"

## Region specifics
rdm_region_discovery_verticies_file="regions/discovery_region_verticies.txt"
rdm_region_load_verticies_file="regions/load_region_verticies.txt"
rdm_region_dump_verticies_file="regions/dump_region_verticies.txt"

## Authorization.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_site_configured_for_hauling.py \
    --env "$env" \
    --dc "$dc" \
    --log_level "$log_level" \
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
    --site_contact_phone "$site_contact_phone" \
    --site_auth_code "$site_auth_code" \
    --rdm_region_discovery_verticies_file "$rdm_region_discovery_verticies_file" \
    --rdm_region_load_verticies_file "$rdm_region_load_verticies_file" \
    --rdm_region_dump_verticies_file "$rdm_region_dump_verticies_file" 
    