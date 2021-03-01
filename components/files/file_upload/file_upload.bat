@echo off
rem # Batch script to upload a file.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

set file_name="file_to_upload.txt"
set file_uuid=""
set parent_uuid=""

rem ## Authentication
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_upload.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --file_name %file_name% ^
    --file_uuid %file_uuid% ^
    --parent_uuid %parent_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%