@echo off
rem ## Batch file to run all examples in this directory

CALL :run_smartview_component "smartview_app_list"

goto:eof
:run_smartview_component <component>
cd %~1
echo.
echo ********* Running smartview component %~1 *********
echo.
call %~1.bat
cd ..
EXIT /B 0