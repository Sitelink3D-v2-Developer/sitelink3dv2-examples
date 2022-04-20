@echo off
rem ## Batch file to run all examples in this directory

CALL :run_rdm_component "rdm_list"
cd rdm_create
CALL :run_rdm_component "delay_create"
CALL :run_rdm_component "material_create"
CALL :run_rdm_component "operator_create"
CALL :run_rdm_component "region_create"
cd ..
cd rdm_parameters
CALL :run_rdm_component "rdm_pagination"
cd ..

goto:eof
:run_rdm_component <component>
cd %~1
echo.
echo ********* Running rdm component %~1 *********
echo.
call %~1.bat
cd ..
EXIT /B 0
