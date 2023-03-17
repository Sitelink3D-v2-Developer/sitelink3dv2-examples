@echo off
rem ## Batch file to stream information about the live machine kinematic state.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

set machine_resource_configuration_file="resource_configurations/haul_truck.resource_configuration.json"

python create_and_connect_machine_to_site.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% ^
    --machine_resource_configuration_file %machine_resource_configuration_file%
    