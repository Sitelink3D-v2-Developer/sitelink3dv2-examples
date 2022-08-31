@echo off
rem ## Batch file to create a site ready to connect Topcon Haul App clients to.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Site creation specifics.
rem # The owner identifier is obtained using the process described at https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-examples#owner-identifier
set site_owner_uuid="" 

set site_name="API Hauling Site"
set site_latitude="-27.979320763437187" 
set site_longitude="153.40316555667877"
set site_timezone="Australia/Brisbane"

set site_contact_name="Joe Burger"
set site_contact_email="jb@jb.com"
set site_contact_phone="123-456-7890"

set site_auth_code="123123"

rem ## Region specifics
set rdm_region_discovery_verticies_file="regions/discovery_region_verticies.txt"
set rdm_region_load_verticies_file="regions/load_region_verticies.txt"
set rdm_region_dump_verticies_file="regions/dump_region_verticies.txt"

rem ## Authorization.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_site_configured_for_hauling.py ^
    --env %env% ^
    --dc %dc% ^
    --site_owner_uuid %site_owner_uuid% ^
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
    --site_contact_phone %site_contact_phone% ^
    --site_auth_code %site_auth_code% ^
    --rdm_region_discovery_verticies_file %rdm_region_discovery_verticies_file% ^
    --rdm_region_load_verticies_file %rdm_region_load_verticies_file% ^
    --rdm_region_dump_verticies_file %rdm_region_dump_verticies_file% 
