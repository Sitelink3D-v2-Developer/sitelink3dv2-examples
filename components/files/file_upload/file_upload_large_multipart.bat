@echo off
rem ## Batch script to upload a large file that must be sent in multiple parts. Sitelink3D v2 will reject files/parts larger than 10485760 bytes.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

set file_name="11,000KB_file_to_upload"
set file_parent_uuid=""

rem ## There are two domains within which files are stored in Sitelink3D v2.
rem # set domain="file_system" to access general files that are visible on the "Site Files" tab in the File Manager.
rem # set domain="operator" to access topo data files from machines that are visible on the "Operator Files" tab in the File Manager.
rem # See the file_operator_upload.bat file for an example of uploading to the operator domain.
set domain="file_system" 

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_upload.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --file_name %file_name% ^
    --file_parent_uuid %file_parent_uuid% ^
    --domain %domain% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    