#!/bin/bash
## Shell script to create a new operator at a site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Operator specifics
rdm_operator_first_name="John"
rdm_operator_second_name="Smith"
rdm_operator_code="JS01"

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
    --log_level "$log_level" \
    --rdm_operator_first_name "$rdm_operator_first_name" \
    --rdm_operator_second_name "$rdm_operator_second_name" \
    --rdm_operator_code "$rdm_operator_code" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
