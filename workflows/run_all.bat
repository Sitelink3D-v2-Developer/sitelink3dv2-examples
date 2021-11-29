@echo off
rem ## Batch file to run all examples in this directory

CALL :run_workflow "create_and_download_haul_report_gpx_trails"
CALL :run_workflow "create_and_download_report"
CALL :run_workflow "create_site_configured_for_hauling"
CALL :run_workflow "create_task_from_design_file"
CALL :run_workflow "download_device_design_data_as_landxml"
CALL :run_workflow "download_operator_pt3_files_as_landxml"
cd files
CALL :run_workflow "upload_and_query_files_and_folders_under_specific_parent"
CALL :run_workflow "upload_and_query_files_with_multiple_versions"
cd ..

goto:eof
:run_workflow <workflow>
cd %~1
echo.
echo ********* Running workflow %~1 *********
echo.
call %~1.bat
cd ..
EXIT /B 0
