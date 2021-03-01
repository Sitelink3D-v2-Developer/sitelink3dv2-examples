@echo off
rem # Batch file to create a folder.

rem ## Settings for the site:
set env="prod"
set dc="us"
set site_id="04c5919236b90436ee8ac715a230ebadc0385c5a9431638a4992d05290aeec97"

set folder_name="86383009-339a-42e9-9c4c-9f78d81f9a16"
set folder_uuid="86383009-339a-42e9-9c4c-9f78d81f9a16"
set parent_uuid=""

rem ## Authentication
set jwt=""
rem # - or -
set oauth_id="108bcc44-367b-439d-ac5f-44daeca73fda"
set oauth_secret="49f260e5-b387-4ba6-805c-cb9c19add625"
set oauth_scope="cab033391c5b6b96c01ec0991c71e28e"

python folder_create.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --folder_name %folder_name% ^
    --folder_uuid %folder_uuid% ^
    --parent_uuid %parent_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%