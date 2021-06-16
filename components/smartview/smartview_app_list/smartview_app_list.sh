#!/bin/bash
# Shell file to list the available smartview applications, their versions and some descriptive information.

env="qa"
dc="us"

exec python smartview_app_list.py \
    --dc "$dc" \
    --env "$env" 
    