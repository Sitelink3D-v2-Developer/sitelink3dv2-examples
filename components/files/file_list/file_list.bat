@echo off
rem # Batch file to list files and folders both archived and unarchived at a site.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

set page_limit="100"
rem ## uuid
set start=""


rem ## Authentication
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_list.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --start %start% ^
    --page_limit %page_limit% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
