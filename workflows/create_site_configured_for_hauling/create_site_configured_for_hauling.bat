@echo off
rem ## Batch file to create a site ready to connect Topcon Haul App clients to.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Site creation specifics.
rem # run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console to obtain the owner / organization identifier.
set owner_id="" 

set site_name="API Hauling Site"
set site_latitude="-27.979320763437187" 
set site_longitude="153.40316555667877"
set site_timezone="Australia/Brisbane"

set site_contact_name="Joe Burger"
set site_contact_email="jb@jb.com"
set site_contact_phone="123-456-7890"

set site_auth_code="123123"

rem ## Region specifics
set region_discovery_file="regions/discovery_region_verticies.txt"
set region_load_file="regions/load_region_verticies.txt"
set region_dump_file="regions/dump_region_verticies.txt"

rem ## Authorization.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""

python create_site_configured_for_hauling.py ^
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
    --site_contact_phone %site_contact_phone% ^
    --site_auth_code %site_auth_code% ^
    --region_discovery_verticies_file %region_discovery_file% ^
    --region_load_verticies_file %region_load_file% ^
    --region_dump_verticies_file %region_dump_file% 
