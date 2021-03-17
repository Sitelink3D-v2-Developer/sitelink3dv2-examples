#!/bin/bash
# Shell file to upload a file containing design data, interrogate the file for design features, import the features, create a design set containing those features and contain a task referencing that design set.

## Settings for the site
env="qa"
dc="us"
site_id=""

## Authentication
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python create_task_from_design_file.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"