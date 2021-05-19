@echo off
rem # Batch script to create a new material at a Sitelink3D v2 site.

rem ## Settings for the site
set env="qa"
set dc="us"
set site_id=""

rem ## Material specifics
set material_name="API Material"

rem ## Authentication
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python material_create.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --material_name %material_name% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%