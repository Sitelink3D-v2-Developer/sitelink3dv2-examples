@echo off
rem ## Batch file to exchange oauth client credentials for an API token.

rem ## Settings for the environment.
set env="qa"
set dc="us"

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem # Authorization
set oauth_id=""
set oauth_secret=""
set oauth_scope="" 

python get_token.py ^
    --env %env% ^
    --dc %dc% ^
    --log_level %log_level% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
    