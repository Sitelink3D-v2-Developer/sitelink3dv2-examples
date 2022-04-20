@echo off
rem ## Batch script to create a new delay at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Delay specifics
set delay_name="Traffic"
set delay_code="D01"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python delay_create.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --delay_name %delay_name% ^
    --delay_code %delay_code% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    