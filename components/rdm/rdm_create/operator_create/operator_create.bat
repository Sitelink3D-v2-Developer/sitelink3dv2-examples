@echo off
rem ## Batch script to create a new operator at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem ## Operator specifics
set rdm_operator_first_name="John"
set rdm_operator_second_name="Smith"
set rdm_operator_code="JS01"

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
    --log_level %log_level% ^
    --rdm_operator_first_name %rdm_operator_first_name% ^
    --rdm_operator_second_name %rdm_operator_second_name% ^
    --rdm_operator_code %rdm_operator_code% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%