@echo off
rem ## Batch script to download a file.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Settings specific to this script.
rem # File representations in RDM look like the following
rem # {
rem #     "id": "a5a6c65d-6f65-49ca-b5a8-405ae4e2e4e9",
rem #     "key": [
rem #         "47fdb852-3d15-481f-b17d-0a8c2dfa6242",
rem #         "fs::file",
rem #         "MyFile.txt"
rem #     ],
rem #     "value": {
rem #         "_at": 1662123399568,
rem #         "_id": "a5a6c65d-6f65-49ca-b5a8-405ae4e2e4e9",
rem #         "_rev": "134a6553-8523-4aee-8534-db274b946ee5",
rem #         "_type": "fs::file",
rem #         "name": "MyFile.txt",
rem #         "parent": "47fdb852-3d15-481f-b17d-0a8c2dfa6242",
rem #         "size": 10378,
rem #         "uuid": "e09b0223-72bc-40f6-a998-2191dda0c67b"
rem #     }
rem # }
rem # 
rem # provide the ["value"]["uuid"] value for "file_uuid" below to download the file
rem # additionally provide the ["id"] value for "file_id" below to allow this script to name the file according to ["value"]["name"] 
set file_uuid=""
set file_id=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python file_download.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --file_uuid %file_uuid% ^
    --file_id %file_id% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    