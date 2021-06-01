@echo off
rem # Batch file to create a folder.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

set folder_name=""
set folder_uuid=""
set parent_uuid=""

rem ## Auth
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python folder_create.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --folder_name %folder_name% ^
    --folder_uuid %folder_uuid% ^
    --parent_uuid %parent_uuid% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%