@echo off
rem # Batch file to list the available smartview applications, their versions and some descriptive information.

set env="qa"
set dc="us"

python smartview_app_list.py ^
    --dc %dc% ^
    --env %env%
    