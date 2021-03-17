#!/bin/bash
# Shell file to exchange oauth client credentials for an API token.

## Settings for the site:
env="qa"
dc="us"

## Authentication
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python get_token.py \
    --dc "$dc" \
    --env "$env" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"