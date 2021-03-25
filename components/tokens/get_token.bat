@echo off
rem # Batch file to exchange oauth client credentials for an API token.

set env="qa"
set dc="us"

rem # Authentication
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python get_token.py ^
    --dc %dc% ^
    --env %env% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%