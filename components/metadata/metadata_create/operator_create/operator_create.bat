@echo off
rem ## Batch script to create a new operator at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Operator specifics
set operator_first_name="John"
set operator_last_code="Smith"
set operator_code="JS01"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python operator_create.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --operator_first_name %operator_first_name% ^
    --operator_last_name %operator_last_code% ^
    --operator_code %operator_code% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%