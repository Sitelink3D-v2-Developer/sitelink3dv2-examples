#!/bin/bash
## Shell file to create a site ready to connect Topcon Haul App clients to.

## Settings for the site
env="qa"
dc="us"
site_id="fdc59e465e0476fbf5bebc1314bf73c23b7ee0c1a095716b57a7440e1db4cd33"

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

file_name="ortho_file.tif"

## Authorization.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python upload_map_tile_overlay.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --file_name "$file_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
    