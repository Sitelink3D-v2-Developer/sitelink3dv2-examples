@echo off
rem ## Batch script to download design data generated on machines as landxml files.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

set page_limit="200"
set start=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python monitor_device_design_data.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --start %start% ^
    --page_limit %page_limit% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%