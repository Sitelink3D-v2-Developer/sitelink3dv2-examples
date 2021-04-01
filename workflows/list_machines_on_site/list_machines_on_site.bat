@echo off
rem # Batch file to run a number of reports, track their status and download the results as files.

rem ## Settings for the site:
set env="prod"
set dc="us"
set site_id="04c5919236b90436ee8ac715a230ebadc0385c5a9431638a4992d05290aeec97"

rem ## Authentication
set oauth_id="108bcc44-367b-439d-ac5f-44daeca73fda"
set oauth_secret="49f260e5-b387-4ba6-805c-cb9c19add625"
set oauth_scope="cab033391c5b6b96c01ec0991c71e28e"

python list_machines_on_site.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope% 
    