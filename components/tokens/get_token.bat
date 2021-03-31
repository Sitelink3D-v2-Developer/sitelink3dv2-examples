@echo off
rem # Batch file to exchange oauth client credentials for an API token.

set env="prod"
set dc="us"

rem # Authentication
set oauth_id="108bcc44-367b-439d-ac5f-44daeca73fda"
set oauth_secret="49f260e5-b387-4ba6-805c-cb9c19add625"
set oauth_scope="6f5f9b4dfe16aaeac3cf438e0259d63d"

python get_token.py ^
    --dc %dc% ^
    --env %env% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%