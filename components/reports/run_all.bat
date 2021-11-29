@echo off
rem ## Batch file to run all examples in this directory

CALL :run_report_component "report_download"
CALL :run_report_component "report_list"

goto:eof
:run_report_component <component>
cd %~1
echo.
echo ********* Running report component %~1 *********
echo.
call %~1.bat
cd ..
EXIT /B 0