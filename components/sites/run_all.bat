@echo off
rem ## Batch file to run all examples in this directory

CALL :run_site_component "site_create"
CALL :run_site_component "site_list"

goto:eof
:run_site_component <component>
cd %~1
echo.
echo ********* Running site component %~1 *********
echo.
call %~1.bat
cd ..
EXIT /B 0
