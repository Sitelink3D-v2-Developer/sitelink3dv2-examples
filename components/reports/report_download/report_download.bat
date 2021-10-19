@echo off
rem ## Batch file to download a report at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Settings specific to this script.
rem # report_url will take the form "https://us-api.sitelink.topcon.com:443/sparkreports/v1/sites/da947..358f/jobs/90e..11ec-935b-02..34e/hauls"
set report_url=""
set report_name=""
set page_limit="500"
set start=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python report_download.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --page_limit %page_limit% ^
    --start %start% ^
    --report_url %report_url% ^
    --report_name %report_name% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
