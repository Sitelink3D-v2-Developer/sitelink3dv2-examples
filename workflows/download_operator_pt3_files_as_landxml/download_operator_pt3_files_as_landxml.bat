@echo off
rem ## Batch script to download operator pt3 files as landxml files.

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

python download_operator_pt3_files_as_landxml.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
