@echo off
rem ## Batch script to upload a file to the "operator" domain. The operator domain contains topo data generated by connected machines.
rem # This script can be used to send topo data to machines by targeting the operator active in that machine. 
rem # Files uploaded by this script are visible in the Sitelink3D v2 web site File Manager on the "Operator Files" tab.
rem # This script is identical to the file_upload.bat example aside from:
rem # 1. The target domain is configured as "operator" rather than "file_system" which Sitelink3D v2 interprets as operator topo data.
rem # 2. The sample file to upload is a PT3 point file, typical of one created on a machine by surveying topo points into a layer.
rem # 3. Additional comments are provided below that describe how the operator uuid to associate the uploaded file with is determined.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

set file_name="My_Operator_Data.pt3"
set file_uuid=""

rem # A parent_uuid is REQUIRED when writing to the "operator" domain. This uuid determines the target operator folder on the "Operator Files" tab.
rem # A parent_uuid is NOT REQUIRED when writing to the "file_system" domain.
rem # To find the uuid for an existing operator, perform the following steps:
rem # 1. Navigate this repo to the file components/metadata/metadata_list/metadata_list.py and ensure the logging level is set to logging.DEBUG.
rem # 2. Populate the wrapper script suitable for you platform (metadata_list.bat or metadata_list.sh) with the details of your site and credentials.
rem # 3. Run the wrapper script to list all metadata at your site. Redirect the output to a file to make the contents easy to inspect.
rem # 4. Search the output file for the operators available at the site and identify the associated id field for the operator of interest as follows.
rem # 5. Copy the operator id into the "parent_uuid" field in this file below this comment block.
rem #
rem # > 2021-07-13 14:29:29,806 metadata_list INFO main:   Found Operator 'John Galt'.
rem # > 2021-07-13 14:29:29,806 metadata_list DEBUG main:   {
rem #     "id": "187d83e1-465b-48de-bed8-cef49e8d678a",
rem #     "key": [
rem #         "Galt",
rem #         "John"
rem #     ],
rem #     "value": {
rem #         "_at": 1625184640699,
rem #         "_id": "187d83e1-465b-48de-bed8-cef49e8d678a",
rem #         "_rev": "f0d091ae-6f8b-43c7-bef2-a8335b673f90",
rem #         "_type": "sl::operator",
rem #         "firstName": "John",
rem #         "lastName": "Galt"
rem #     }
rem # }

set parent_uuid=""

rem ## There are two domains within which files are stored in Sitelink3D v2.
rem # use domain="file_system" to access general files that are visible on the "Site Files" tab in the File Manager.
rem # use domain="operator" to access topo data files from machines that are visible on the "Operator Files" tab in the File Manager.
rem # See the file_upload.bat file for an example of uploading to the file_system domain.
set domain="operator" 

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
    --file_uuid %file_uuid% ^
    --parent_uuid %parent_uuid% ^
    --domain %domain% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    