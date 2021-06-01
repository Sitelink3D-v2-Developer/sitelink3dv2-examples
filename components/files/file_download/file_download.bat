@echo off
rem # Batch script to download a file.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

set file_uuid=""

rem ## Authentication
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_download.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --file_uuid %file_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%