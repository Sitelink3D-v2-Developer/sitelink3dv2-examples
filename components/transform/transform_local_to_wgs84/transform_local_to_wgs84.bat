@echo off
rem ## Batch file to convert site local grid points into cartesian (ECEF) and geodetic (WGS84) points in an output file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Settings specific to this script.
set local_position_points_file="tps-bris.points.json"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python transform_local_to_wgs84.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --local_position_points_file %local_position_points_file% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%