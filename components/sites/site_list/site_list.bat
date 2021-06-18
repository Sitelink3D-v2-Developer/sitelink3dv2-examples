@echo off
rem ## Batch file to list the sites at an organization / owner.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Settings specific to this script.
rem # run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console to obtain the owner / organization identifier.
set owner_id=""

rem ## Authorization
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""

python site_list.py ^
    --env %env% ^
    --dc %dc% ^
    --owner_id %owner_id% ^
    --jwt %jwt% 
    