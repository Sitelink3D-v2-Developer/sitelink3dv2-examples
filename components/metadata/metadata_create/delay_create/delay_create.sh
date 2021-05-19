# Shell script to create a new delay at a Sitelink3D v2 site.

## Settings for the site
env="qa"
dc="us"
site_id=""

## Delay specifics
delay_name="Traffic"
delay_code="D01"

rem ## Auth
oauth_id=""
oauth_secret=""
oauth_scope=""

exec python delay_create.py \
    --dc "$dc" \
    --env "$env" \
    --site_id "$site_id" \
    --delay_name "$delay_name" \
    --delay_code "$delay_code" \
    --oauth_id "$oauth_id" \
    --oauth_secret "$oauth_secret" \
    --oauth_scope "$oauth_scope"