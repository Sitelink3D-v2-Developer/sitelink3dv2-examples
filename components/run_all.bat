@echo off
rem ## Batch file to run all examples in this directory

CALL :run_component "files"
CALL :run_component "metadata"
CALL :run_component "reports"
CALL :run_component "sites"
CALL :run_component "smartview"
CALL :run_component "tokens"

goto:eof
:run_component <component>
cd %~1
call run_all.bat
cd ..
EXIT /B 0
