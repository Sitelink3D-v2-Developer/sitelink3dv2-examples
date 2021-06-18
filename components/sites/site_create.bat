@echo off
rem ## Batch file to create a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Site creation specifics.
rem # run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console to obtain the owner / organization identifier.
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

python site_create.py ^
    --env %env% ^
    --dc %dc% ^
    --owner_id %owner_id% ^
    --jwt %jwt% ^
    --site_name %site_name% ^
    --site_latitude %site_latitude% ^
    --site_longitude %site_longitude% ^
    --site_timezone %site_timezone% ^
    --site_contact_name %site_contact_name% ^
    --site_contact_email %site_contact_email% ^
    --site_contact_phone %site_contact_phone%
    