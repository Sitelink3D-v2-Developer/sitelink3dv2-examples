@echo off
rem # Batch file to exchange oauth client credentials for an API token.

set env="qa"
set dc="us"

rem # Authentication
set oauth_id="2dc51e38-8b90-479d-a45a-6be25284e465"
set oauth_secret="d481ab84-056c-454d-9615-f871a5f8558a"
set oauth_scope="c805593d6a103162fb5df196877ee7df"

python get_token.py ^
    --dc %dc% ^
    --env %env% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%