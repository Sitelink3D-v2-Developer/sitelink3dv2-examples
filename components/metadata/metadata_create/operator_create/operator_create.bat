@echo off
rem # Batch script to create a new operator at a Sitelink3D v2 site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Operator specifics
set operator_first_name="John"
set operator_last_code="Smith"
set operator_code="JS01"

rem ## Auth
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python operator_create.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --operator_first_name %operator_first_name% ^
    --operator_last_name %operator_last_code% ^
    --operator_code %operator_code% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%