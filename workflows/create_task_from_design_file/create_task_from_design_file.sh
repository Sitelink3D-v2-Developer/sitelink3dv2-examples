#!/bin/bash
## Shell script to upload a file containing design data, interrogate the file for design features, import the features, create a design set containing those features and create a task referencing that design set.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

design_file_name="tps-bris.tp3"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_task_from_design_file.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --design_file_name "$design_file_name" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
