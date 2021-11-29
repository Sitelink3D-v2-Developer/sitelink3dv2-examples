@echo off
rem ## Batch file to run all examples in this directory

CALL :run_nested_file_component "file_download"
CALL :run_nested_file_component "file_features"
CALL :run_nested_file_component "file_list"
CALL :run_nested_file_component "folder_create"
cd file_upload
CALL :run_file_component "file_upload"
CALL :run_file_component "file_operator_upload"
cd ..

goto:eof
:run_nested_file_component <component>
cd %~1
call :run_file_component %~1
cd ..
EXIT /B 0

:run_file_component <component>
echo.
echo ********* Running file component %~1 *********
echo.
call %~1.bat
EXIT /B 0