@echo off
rem # Batch file to stream information about the machines connected to a site.

rem ## Settings for the site:
set env="prod"
set dc="us"
set site_id=""

rem ## Authentication
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python list_machines_on_site.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    