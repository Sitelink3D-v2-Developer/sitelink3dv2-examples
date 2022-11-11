@echo off
rem # Batch file to retore a specified site.

rem ## Settings for the environment.
set env="qa"
set site_id=""

set operation="unarchive"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python site_archive_restore.py ^
    --env %env% ^
    --site_id %site_id% ^
    --operation %operation% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
