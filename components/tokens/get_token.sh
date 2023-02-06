#!/bin/bash
## Shell file to exchange oauth client credentials for an API token.

## Settings for the environment.
env="qa"
dc="us"

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Authorization
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python get_token.py \
    --env "$env" \
    --dc "$dc" \
    --log_level "$log_level" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
