@echo off
rem # Batch file to stream information about the weight assignment payload data sent from loading machines to haul trucks at a site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Authentication
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python stream_machine_weight_assignments.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    