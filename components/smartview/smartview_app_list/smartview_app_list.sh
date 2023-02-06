#!/bin/bash
## Shell file to list the available smartview applications, their versions and some descriptive information.

env="qa"
dc="us"

## Log configuraiton. 
# critical=50, error=40, warning=30, info=20, debug=10
log_level=20

exec python smartview_app_list.py \
    --env "$env" \
    --dc "$dc" \
    --log_level "$log_level"    
    