#!/bin/bash
## Shell file to list the sites at an organization / owner.

## Settings for the environment.
env="qa"
dc="us"

## Settings specific to this script.
# The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
# This parameter is optional.
site_owner_uuid=""

## optionally sort the results. sort_field may be either "rdm_name" or "create_timestamp_ms".
# sorted results are ascending by default. ordering can be specified with sort_order="+" for ascending or sort_order="-" for descending. 
# sort_field="create_timestamp_ms"
# sort_order="+"
sort_field="create_timestamp_ms"
sort_order="+"

page_limit="100"
start=""

## optionally filter results. 
# to filter site names containing "haul" with owner gmail accounts created since start of 2021 with medium cell size based in US:
# filter_name_includes="*haul*"
# filter_owner_email_includes="*gmail*"
# filter_created_since_epoch="1609423200000"
# filter_cell_size_equals="medium"
# filter_data_center_equals="us"

filter_name_includes=""
filter_owner_email_includes=""
filter_created_since_epoch=""
filter_cell_size_equals=""
filter_data_center_equals=""

## Authorization
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python site_list.py \
    --env "$env" \
    --dc "$dc" \
    --site_owner_uuid "$site_owner_uuid" \
    --sort_field "$sort_field" \
    --sort_order "$sort_order" \
    --page_limit "$page_limit" \
    --start "$start" \
    --filter_name_includes "$filter_name_includes" \
    --filter_owner_email_includes "$filter_owner_email_includes" \
    --filter_created_since_epoch "$filter_created_since_epoch" \
    --filter_cell_size_equals "$filter_cell_size_equals" \
    --filter_data_center_equals "$filter_data_center_equals" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope" 
    