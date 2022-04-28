#!/bin/bash
## Shell file to convert site local grid points into cartesian (ECEF) and geodetic (WGS84) points in an output file.

## ## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Settings specific to this script.
transform_local_position_points_file="tps-bris.points.json"

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python transform_local_to_wgs84.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --transform_local_position_points_file "$transform_local_position_points_file" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"