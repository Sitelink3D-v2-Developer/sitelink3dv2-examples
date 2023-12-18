@echo off
rem ## Batch script to list the road trucks known at a site, create a new one, list its properties by name and unique ID, and then update its target weight property.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=10

rem ## Road truck specifics
set rdm_road_truck_name="LV-001 (truck)"
set rdm_road_truck_code="001a"
set rdm_road_truck_target="2.5"
set rdm_road_truck_target_update="5.5"
set rdm_road_truck_tare="5.0"

set rdm_road_trailer_name="LV-001 (trailer)"
set rdm_road_trailer_code="001b"
set rdm_road_trailer_target="4.5"
set rdm_road_trailer_tare="5.0"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_search_and_update_road_truck.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --rdm_road_truck_name %rdm_road_truck_name% ^
    --rdm_road_truck_code %rdm_road_truck_code% ^
    --rdm_road_truck_target %rdm_road_truck_target% ^
    --rdm_road_truck_target_update %rdm_road_truck_target_update% ^
    --rdm_road_truck_tare %rdm_road_truck_tare% ^
    --rdm_road_trailer_name %rdm_road_trailer_name% ^
    --rdm_road_trailer_code %rdm_road_trailer_code% ^
    --rdm_road_trailer_target %rdm_road_trailer_target% ^
    --rdm_road_trailer_tare %rdm_road_trailer_tare% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
