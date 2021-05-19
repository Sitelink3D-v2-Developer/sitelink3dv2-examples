#!/bin/bash
# Shell script to create a new region at a Sitelink3D v2 site.

## Settings for the site:
env="qa"
dc="us"
site_id=""

## Region specifics
region_name="API Region"
region_verticies_file="verticies/brisbane.txt"

## Auth
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python region_create.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --region_name "$region_name" \
    --region_verticies_file "$region_verticies_file" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"