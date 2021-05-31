@echo off
rem # Batch file to list the sites at an organization / owner.

rem ## Settings for the site:
set env="qa"
set dc="us"
rem # run `SitelinkFrontend.core.store.getState().app.owner.ownerId` in your browser developer console for this value
set owner_id=""

rem ## Auth
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console for this value
set jwt=""

python site_list.py ^
    --dc %dc% ^
    --env %env% ^
    --owner_id %owner_id% ^
    --jwt %jwt%
    