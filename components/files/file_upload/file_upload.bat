@echo off
rem ## Batch script to upload a file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

set file_name="file_to_upload.txt"
set file_uuid=""
set parent_uuid=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_upload.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --file_name %file_name% ^
    --file_uuid %file_uuid% ^
    --parent_uuid %parent_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    