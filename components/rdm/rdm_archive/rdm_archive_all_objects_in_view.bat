@echo off
rem # Batch file to archive all objects in a specified RDM view.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem # Use the components/rdm/rdm_list example to discover the domains and associated views at your site.
set rdm_view="v_sl_delay_by_name"
set rdm_domain="sitelink"
set operation="archive"

set page_limit="50"
set start=""

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python rdm_archive_or_restore_all_objects_in_view.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --start %start% ^
    --page_limit %page_limit% ^
    --rdm_view %rdm_view% ^
    --rdm_domain %rdm_domain% ^
    --operation %operation% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%
