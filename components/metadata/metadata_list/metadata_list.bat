@echo off
rem # Batch file to list all metadata views and all data provided by those views at all domains at a sitelink site

rem ## Settings for the site:
set env="prod"
set dc="us"
set site_id=""

set page_limit="200"
set start=""

rem ## Auth
set jwt=""

python metadata_list.py ^
    --dc %dc% ^
    --env %env% ^
    --site_id %site_id% ^
    --start %start% ^
    --page_limit %page_limit% ^
    --jwt %jwt%