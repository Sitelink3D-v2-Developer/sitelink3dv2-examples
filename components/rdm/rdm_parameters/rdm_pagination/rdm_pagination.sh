#!/bin/bash
## Shell file to list RDM data from of the specified view at the specified page size and request subsequent pages until all data is received.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

# Use the components/rdm/rdm_list example to discover the domains and associated views at your site.
rdm_view="v_sl_delay_by_name"
rdm_domain="sitelink"

page_limit="5"
start=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python rdm_pagination.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --start "$start" \
    --page_limit "$page_limit" \
    --rdm_view "$rdm_view" \
    --rdm_domain "$rdm_domain" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
