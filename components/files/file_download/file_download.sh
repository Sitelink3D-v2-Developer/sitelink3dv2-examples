#!/bin/bash
## Shell file to download a file.

## Settings for the environment.
env="qa"
dc="us"
site_id=""

## Settings specific to this script.
# File representations in RDM look like the following
# {
#     "id": "a5a6c65d-6f65-49ca-b5a8-405ae4e2e4e9",
#     "key": [
#         "47fdb852-3d15-481f-b17d-0a8c2dfa6242",
#         "fs::file",
#         "MyFile.txt"
#     ],
#     "value": {
#         "_at": 1662123399568,
#         "_id": "a5a6c65d-6f65-49ca-b5a8-405ae4e2e4e9",
#         "_rev": "134a6553-8523-4aee-8534-db274b946ee5",
#         "_type": "fs::file",
#         "name": "MyFile.txt",
#         "parent": "47fdb852-3d15-481f-b17d-0a8c2dfa6242",
#         "size": 10378,
#         "uuid": "e09b0223-72bc-40f6-a998-2191dda0c67b"
#     }
# }
# 
# provide the ["value"]["uuid"] value for "file_uuid" below to download the file
# additionally provide the ["id"] value for "file_id" below to allow this script to name the file according to ["value"]["name"] 
file_uuid=""
file_id=""

## Authorization. OAuth credentials are used if the JWT string is empty.
# run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
jwt=""
# - or -
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python file_download.py \
    --env "$env" \
    --dc "$dc" \
    --site_id "$site_id" \
    --file_uuid "$file_uuid" \
    --file_id "$file_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"
