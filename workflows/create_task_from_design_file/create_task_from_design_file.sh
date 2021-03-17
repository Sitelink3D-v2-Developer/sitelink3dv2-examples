#!/bin/bash
# Shell file to upload a file containing design data, interrogate the file for design features, import the features, create a design set containing those features and contain a task referencing that design set.

## Settings for the site
env="qa"
dc="us"
site_id="fdc59e465e0476fbf5bebc1314bf73c23b7ee0c1a095716b57a7440e1db4cd33"

## Authentication
jwt=""
# - or -
oauth_id="2dc51e38-8b90-479d-a45a-6be25284e465"
oauth_secret="d481ab84-056c-454d-9615-f871a5f8558a"
oauth_scope="892e40a954bd5b0dece7ef6e16425450"

exec python create_task_from_design_file.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --jwt "$jwt" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"