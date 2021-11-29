@echo off
rem ## Batch file to list the sites at an organization / owner.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Settings specific to this script.
rem # run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console to obtain the owner / organization identifier.
set owner_id=""

rem ## optionally sort the results. sort_field may be either "rdm_name" or "create_timestamp_ms".
rem # sorted results are ascending by default. ordering can be specified with sort_order="+" for ascending or sort_order="-" for descending. 
set sort_field="create_timestamp_ms"
set sort_order="+"

set page_limit="100"
set start=""

rem ## optionally filter results. 
rem # to filter site names containing "haul" with owner gmail accounts created since start of 2021 with medium cell size based in US:
rem set filter_name_includes="*haul*"
rem set filter_owner_email_includes="*gmail*"
rem set filter_created_since_epoch="1609423200000"
rem set filter_cell_size_equals="medium"
rem set filter_data_center_equals="us"

set filter_name_includes=""
set filter_owner_email_includes=""
set filter_created_since_epoch=""
set filter_cell_size_equals=""
set filter_data_center_equals=""

rem ## Authorization
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python site_list.py ^
    --env %env% ^
    --dc %dc% ^
    --owner_id %owner_id% ^
    --sort_field %sort_field% ^
    --sort_order %sort_order% ^
    --page_limit %page_limit% ^
    --start %start% ^
    --filter_name_includes %filter_name_includes% ^
    --filter_owner_email_includes %filter_owner_email_includes% ^
    --filter_created_since_epoch %filter_created_since_epoch% ^
    --filter_cell_size_equals %filter_cell_size_equals% ^
    --filter_data_center_equals %filter_data_center_equals% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
