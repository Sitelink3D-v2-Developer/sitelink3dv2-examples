#!/bin/bash
## Shell script to create a new mix at a site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Mix specifics
rdm_mix_name="API Mix"

rdm_mix_material_1_uuid=""
rdm_mix_material_1_ratio=2
rdm_mix_material_2_uuid=""
rdm_mix_material_2_ratio=6

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python mix_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --rdm_mix_name "$rdm_mix_name" \
    --rdm_mix_material_1_uuid "$rdm_mix_material_1_uuid" \
    --rdm_mix_material_1_ratio "$rdm_mix_material_1_ratio" \
    --rdm_mix_material_2_uuid "$rdm_mix_material_2_uuid" \
    --rdm_mix_material_2_ratio "$rdm_mix_material_2_ratio" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
