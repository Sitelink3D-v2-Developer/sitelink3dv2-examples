@echo off
rem ## Batch file to run all examples in this directory

CALL :run_token_component "get_token"

goto:eof
:run_token_component <component>
echo.
echo ********* Running token component %~1 *********
echo.
call %~1.bat
EXIT /B 0
