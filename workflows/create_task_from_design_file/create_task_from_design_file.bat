@echo off
rem # Batch file to upload a file containing design data, interrogate the file for design features, import the features, create a design set containing those features and contain a task referencing that design set.

rem ## Settings for the site:
set env="qa"
set dc="us"
set site_id=""

rem ## Authentication
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_task_from_design_file.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
