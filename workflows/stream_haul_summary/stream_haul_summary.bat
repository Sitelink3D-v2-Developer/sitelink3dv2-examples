@echo off
rem # Batch file to stream information about the haul cycle activity at a site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Authentication
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python stream_haul_summary.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    