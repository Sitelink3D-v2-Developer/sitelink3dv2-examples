#!/bin/bash
## Shell file to exchange oauth client credentials for an API token.

## Settings for the environment.
env="qa"
dc="us"

## Authorization
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python get_token.py \
    --env "$env" \
    --dc "$dc" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
