@echo off
rem ## Batch file to list the active and archived files and folders at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem ## Settings specific to this script.
set page_limit="500"
set start=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_list.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --page_limit %page_limit% ^
    --start %start% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
