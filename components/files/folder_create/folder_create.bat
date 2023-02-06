@echo off
rem ## Batch file to create a folder.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

set folder_name="Windows Folder"
set folder_uuid=""
set folder_parent_uuid=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python folder_create.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --folder_name %folder_name% ^
    --folder_uuid %folder_uuid% ^
    --folder_parent_uuid %folder_parent_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
