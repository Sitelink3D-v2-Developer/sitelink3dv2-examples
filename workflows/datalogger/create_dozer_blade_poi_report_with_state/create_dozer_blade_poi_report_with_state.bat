@echo off
rem ## Batch file to read position and state information specific to bulldozers via the datalogger microservice. The output is written to a user specified CSV file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem original dozer activity window in ms from epoch
set startms="1646187249000"
set endms="1646187849394"

set report_file_name="MachineUpdateReport.csv"

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python create_dozer_blade_poi_report_with_state.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --startms %startms% ^
    --endms %endms% ^
    --report_file_name %report_file_name% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    