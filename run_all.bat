@echo off
rem ## Batch file to run all examples in the repository

cd components
call run_all.bat
cd ..

cd workflows
call run_all.bat
cd ..
