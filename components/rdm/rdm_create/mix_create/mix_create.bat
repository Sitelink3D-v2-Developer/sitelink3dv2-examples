@echo off
rem ## Batch script to create a new mix at a site.

rem ## Settings for the environment.
set env="qa"
set dc="us"
set site_id=""

rem ## Log configuraiton. 
rem # critical=50, error=40, warning=30, info=20, debug=10
set log_level=20

rem ## Mix specifics
set rdm_mix_name="API Mix"

set rdm_mix_material_1_uuid=""
set rdm_mix_material_1_ratio=2
set rdm_mix_material_2_uuid=""
set rdm_mix_material_2_ratio=6

rem ## Authorization. OAuth credentials are used if the JWT string is empty.
rem # run `SitelinkFrontend.core.store.getState().app.owner.jwt[0]` in your browser developer console to obtain a JWT.
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""

python mix_create.py ^
    --env %env% ^
    --dc %dc% ^
    --site_id %site_id% ^
    --log_level %log_level% ^
    --rdm_mix_name %rdm_mix_name% ^
    --rdm_mix_material_1_uuid %rdm_mix_material_1_uuid% ^
    --rdm_mix_material_1_ratio %rdm_mix_material_1_ratio% ^
    --rdm_mix_material_2_uuid %rdm_mix_material_2_uuid% ^
    --rdm_mix_material_2_ratio %rdm_mix_material_2_ratio% ^
    --jwt %jwt% ^
    --oauth_id %oauth_id% ^
    --oauth_secret %oauth_secret% ^
    --oauth_scope %oauth_scope%