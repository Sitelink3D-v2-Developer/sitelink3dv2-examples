@echo off
rem ## Batch file to list the current and any historical files used for localization at a site and when those localizations were in use.

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

python list_site_localization_history.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
