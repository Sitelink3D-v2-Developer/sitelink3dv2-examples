#!/bin/bash
# Shell script to create a new operator at a Sitelink3D v2 site.

## Settings for the site:
env="qa"
dc="us"
site_id=""

## Operator specifics
operator_first_name="John"
operator_last_code="Smith"
operator_code="JS01"

## Auth
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python operator_create.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --operator_first_name "$operator_first_name" \
    --operator_last_name "$operator_last_code" \
    --operator_code "$operator_code" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"