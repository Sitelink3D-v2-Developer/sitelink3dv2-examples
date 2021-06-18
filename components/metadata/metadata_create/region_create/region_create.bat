@echo off
rem ## Batch script to create a new region at a Sitelink3D v2 site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Region specifics
set region_name="API Region from Windows"
set region_verticies_file="verticies/brisbane.txt"

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
    --region_name %region_name% ^
    --region_verticies_file %region_verticies_file% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%