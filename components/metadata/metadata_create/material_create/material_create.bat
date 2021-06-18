@echo off
rem ## Batch script to create a new material at a Sitelink3D v2 site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Material specifics
set material_name="API Material"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python material_create.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --material_name %material_name% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%