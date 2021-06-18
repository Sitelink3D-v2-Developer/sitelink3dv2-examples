#!/bin/bash
## Shell script to create a new operator at a Sitelink3D v2 site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Operator specifics
operator_first_name="John"
operator_last_code="Smith"
operator_code="JS01"

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python operator_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --operator_first_name "$operator_first_name" \
    --operator_last_name "$operator_last_code" \
    --operator_code "$operator_code" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
