#!/bin/bash
## Shell file to stream information about the live machine kinematic state.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

machine_resource_configuration_file="resource_configurations/haul_truck.resource_configuration.json"

exec python create_and_connect_machine_to_site.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" \
    --machine_resource_configuration_file "$machine_resource_configuration_file" \
