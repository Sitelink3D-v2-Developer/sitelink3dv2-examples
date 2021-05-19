@echo off
rem # Batch script to create a new delay at a Sitelink3D v2 site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Delay specifics
set delay_name="Traffic"
set delay_code="D01"

rem ## Auth
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python delay_create.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --delay_name %delay_name% ^
    --delay_code %delay_code% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%