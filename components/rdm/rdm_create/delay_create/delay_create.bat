@echo off
rem ## Batch script to create a new delay at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Delay specifics
set rdm_delay_name="Traffic"
set rdm_delay_code="D01"

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
    --rdm_delay_name %rdm_delay_name% ^
    --rdm_delay_code %rdm_delay_code% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    