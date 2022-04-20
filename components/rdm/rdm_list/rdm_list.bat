@echo off
rem # Batch file to list all RDM views and all data provided by those views at all domains at a sitelink site

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

set page_limit="200"
set start=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python rdm_list.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --start %start% ^
    --page_limit %page_limit% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%