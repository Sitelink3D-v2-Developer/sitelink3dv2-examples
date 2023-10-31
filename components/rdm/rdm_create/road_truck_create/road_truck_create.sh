#!/bin/bash
## Shell script to create a new road truck at a site.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

## Road truck specifics
rdm_road_truck_name="Truck 001"
rdm_road_truck_code="001"
rdm_road_truck_target="12.5"
rdm_road_truck_tare="5.0"

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python road_truck_create.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --log_level "$log_level" \
    --rdm_road_truck_name "$rdm_road_truck_name" \
    --rdm_road_truck_code "$rdm_road_truck_code" \
    --rdm_road_truck_target "$rdm_road_truck_target" \
    --rdm_road_truck_tare "$rdm_road_truck_tare" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
