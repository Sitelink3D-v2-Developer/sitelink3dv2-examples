@echo off
rem # Batch file to find a single RDM object represented by the specified UUID in a view at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem # Use the components/metadata/rdm_list example to discover the domains and associated views at your site.
set rdm_view="v_sl_task_by_name"
set rdm_domain="sitelink"
set rdm_object_uuid=""

set page_limit="100"
set start=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python rdm_query_object.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --start %start% ^
    --page_limit %page_limit% ^
    --rdm_view %rdm_view% ^
    --rdm_domain %rdm_domain% ^
    --rdm_object_uuid %rdm_object_uuid% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
