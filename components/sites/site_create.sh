#!/bin/bash
# Shell file to create a site.

## Settings for the site:
env="qa"
dc="us"
owner_id=""

site_name="API Site"
site_latitude=""
site_longitude=""
site_timezone=""

site_contact_name=""
site_contact_email=""
site_contact_phone=""

## Authentication
jwt=""

exec python site_create.py ^
    --dc "$dc" \
    --env "$env" \
    --owner_id "$owner_id" \
    --jwt "$jwt" \
    --site_name "$site_name" \
    --site_latitude "$site_latitude" \
    --site_longitude "$site_longitude" \
    --site_timezone "$site_timezone" \
    --site_contact_name "$site_contact_name" \
    --site_contact_email "$site_contact_email" \
    --site_contact_phone "$site_contact_phone"    