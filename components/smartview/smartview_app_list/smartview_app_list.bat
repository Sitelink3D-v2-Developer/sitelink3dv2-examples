@echo off
rem ## Batch file to list the available smartview applications, their versions and some descriptive information.

set env="qa"
set dc="us"

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

python smartview_app_list.py ^
    --env %env% ^
    --dc %dc% ^
    --log_level %log_level%
    