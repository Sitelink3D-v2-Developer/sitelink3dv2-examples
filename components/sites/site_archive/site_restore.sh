#!/bin/bash
## Shell file to retore a specified site.

## Settings for the environment.
env="qa"
site_id=""

operation="unarchive"

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python site_archive_restore.py \
    --env "$env" \
    --site_id "$site_id" \
    --operation "$operation" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
