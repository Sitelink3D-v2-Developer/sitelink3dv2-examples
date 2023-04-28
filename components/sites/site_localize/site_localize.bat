@echo off
rem ## Batch file to localize a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Site localization specifics.
set site_id="" 
set file_id=""
set file_rev=""

rem ## Authorization.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python site_localize.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --file_id %file_id% ^
    --file_rev %file_rev% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    