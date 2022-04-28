@echo off
rem ## Batch file to upload a file containing design data, interrogate the file for design features, import the features, create a design set containing those features and create a task referencing that design set.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

set file_name="tps-bris.tp3"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_task_from_design_file.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --file_name %file_name% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
