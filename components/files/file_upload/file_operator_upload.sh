#!/bin/bash
## Shell script to upload a file to the "operator" domain. The operator domain contains topo data generated by connected machines.
# This script can be used to send topo data to machines by targeting the operator active in that machine. 
# Files uploaded by this script are visible in the Sitelink3D v2 web site File Manager on the "Operator Files" tab.
# This script is identical to the file_upload.sh example aside from:
# 1. The target domain is configured as "operator" rather than "file_system" which Sitelink3D v2 interprets as operator topo data.
# 2. The sample file to upload is a PT3 point file, typical of one created on a machine by surveying topo points into a layer.
# 3. Additional comments are provided below that describe how the operator uuid to associate the uploaded file with is determined.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

file_name="My_Operator_Data.pt3"

# A parent_uuid is REQUIRED when writing to the "operator" domain. This uuid determines the target operator folder on the "Operator Files" tab.
# A parent_uuid is NOT REQUIRED when writing to the "file_system" domain.
# To find the uuid for an existing operator, perform the following steps:
# 1. Navigate this repo to the file components/metadata/metadata_list/metadata_list.py and ensure the logging level is set to logging.DEBUG.
# 2. Populate the wrapper script suitable for your platform (metadata_list.bat or metadata_list.sh) with the details of your site and credentials.
# 3. Run the wrapper script to list all metadata at your site. Redirect the output to a file to make the contents easy to inspect.
# 4. Search the output file for the operators available at the site and identify the associated id field for the operator of interest as follows.
# 5. Copy the operator id into the "parent_uuid" field in this file below this comment block.
#
# > 2021-07-13 14:29:29,806 metadata_list INFO main:   Found Operator 'John Galt'.
# > 2021-07-13 14:29:29,806 metadata_list DEBUG main:   {
#     "id": "187d83e1-465b-48de-bed8-cef49e8d678a",
#     "key": [
#         "Galt",
#         "John"
#     ],
#     "value": {
#         "_at": 1625184640699,
#         "_id": "187d83e1-465b-48de-bed8-cef49e8d678a",
#         "_rev": "f0d091ae-6f8b-43c7-bef2-a8335b673f90",
#         "_type": "sl::operator",
#         "firstName": "John",
#         "lastName": "Galt"
#     }
# }

parent_uuid=""

## There are two domains within which files are stored in Sitelink3D v2.
# use domain="file_system" to access general files that are visible on the "Site Files" tab in the File Manager.
# use domain="operator" to access topo data files from machines that are visible on the "Operator Files" tab in the File Manager.
# See the file_upload.bat file for an example of uploading to the file_system domain.
domain="operator" 

## Authorization. OAuth credentials are used if the JWT string is empty.
## run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_upload.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --file_name "$file_name" \
    --parent_uuid "$parent_uuid" \
    --domain "$domain" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
