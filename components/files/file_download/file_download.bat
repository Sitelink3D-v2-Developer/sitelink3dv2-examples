@echo off
rem ## Batch script to download a file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Settings specific to this script.
set file_uuid=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_download.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --file_uuid %file_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%