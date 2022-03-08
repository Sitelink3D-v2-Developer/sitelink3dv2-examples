@echo off
rem ## Batch file to create a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Site creation specifics.
rem # The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
set owner_id="" 

set site_name="API Site"
set site_latitude=""
set site_longitude=""
set site_timezone=""

set site_contact_name=""
set site_contact_email=""
set site_contact_phone=""

rem ## Authorization.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python site_create.py ^
    --env %env% ^
    --dc %dc% ^
    --owner_id %owner_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% ^
    --site_name %site_name% ^
    --site_latitude %site_latitude% ^
    --site_longitude %site_longitude% ^
    --site_timezone %site_timezone% ^
    --site_contact_name %site_contact_name% ^
    --site_contact_email %site_contact_email% ^
    --site_contact_phone %site_contact_phone%
    