#!/bin/bash
# Shell file to list all metadata views and all data provided by those views at all domains at a sitelink site

# Settings for the site:
env="prod"
dc="us"
site_id=""

page_limit="200"
start=""

## Auth
jwt=""

exec python metadata_list.py \
	--dc "$dc" \
	--env "$env" \
	--site_id "$site_id" \
	--start "$start" \
	--page_limit "$page_limit" \
	--jwt "$jwt"
