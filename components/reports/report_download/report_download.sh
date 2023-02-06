#!/bin/bash
## Shell script to download a report at a site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Settings specific to this script.
# report_url will take the form "https://us-api.sitelink.topcon.com:443/sparkreports/v1/sites/da947..358f/jobs/90e..11ec-935b-02..34e/hauls"
report_url=""
report_name=""
page_limit="500"
start=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python report_download.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --page_limit "$page_limit" \
    --start "$start" \
    --report_url "$report_url" \
    --report_name "$report_name" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"