@echo off
rem ## Batch script to create a new region at a site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem ## Region specifics
set rdm_region_name="API Region from Windows"
set rdm_region_verticies_file="verticies/brisbane.txt"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python region_create.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --rdm_region_name %rdm_region_name% ^
    --rdm_region_verticies_file %rdm_region_verticies_file% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%