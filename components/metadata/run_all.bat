@echo off
rem ## Batch file to run all examples in this directory

CALL :run_metadata_component "metadata_list"
cd metadata_create
CALL :run_metadata_component "delay_create"
CALL :run_metadata_component "material_create"
CALL :run_metadata_component "operator_create"
CALL :run_metadata_component "region_create"
cd ..
cd rdm_parameters
CALL :run_metadata_component "rdm_pagination"
cd ..

goto:eof
:run_metadata_component <component>
cd %~1
echo.
echo ********* Running metadata component %~1 *********
echo.
call %~1.bat
cd ..
EXIT /B 0
