@echo off
rem ## Batch file to list the specified organization / owner details.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem ## Settings specific to this script.
rem # The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
set site_owner_uuid=""

rem ## Authorization
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python owner_get.py ^
    --env %env% ^
    --dc %dc% ^
    --log_level %log_level% ^
    --site_owner_uuid %site_owner_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
