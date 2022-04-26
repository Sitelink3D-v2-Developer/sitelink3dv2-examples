#!/usr/bin/env bash
# This script creates a tree of run_all.bat and run_all.sh scripts in the nested directories.
# It allows all examples to be run sequentially with the following conditions:
# 1. The bat or sh files are first populated with credentials and settings.
# 2. The streaming examples will not naturally terminate so either need to be excluded or run in isolation.

function add_run_all_bat() {
    local batfiles=$(ls *.bat 2>/dev/null|grep -v run_all.bat|grep -v setup.bat)
    local subdirs=$(ls -d */ 2>/dev/null|tr -d /)
    [[ -n "$batfiles$subdirs" ]] || return 1
    local d f
    sed 's/^\s*//' <<END > run_all.bat
    @echo off
    rem ## Batch file to run all examples in this directory
    for /f %%i in (%~f0) do @set me=%%~ni

END
    for d in $subdirs; do
        [[ $d = "*/" ]] && continue
        d=${d%/}
        [[ -d $d ]] || continue
        cd $d
        pwd
        if add_run_all_bat; then
            echo CALL :descend_into '"'$d'"' >> ../run_all.bat
        fi
        cd ..
    done
    for f in $batfiles; do
        [[ -f $f ]] || continue
        echo CALL :run_command '"'$(basename $f .bat)'"' >> run_all.bat
    done
    sed 's/^\s*//' <<END >> run_all.bat
    goto:eof

    :descend_into <component>
    echo.
    echo ********* %me : Running %~1 examples *********
    echo.
    cd %~1
    call run_all.bat
    cd ..
    EXIT /B 0

    :run_command <command>
    echo.
    echo ********* Running %me : component %~1 *********
    echo.
    call %~1.bat
    EXIT /B 0
END
}

function add_run_all_sh() {
    local shfiles=$(ls *.sh 2>/dev/null | grep -v setup.sh | grep -v run_all.sh)
    local subdirs=$(ls -d */ 2>/dev/null|tr -d /)
    [[ -n "$shfiles$subdirs" ]] || return 1

    local d f
    sed 's/^\s*@//' <<'END' > run_all.sh
    @#!/usr/bin/env bash
    @
    @## Batch file to run all examples in this directory
    @me=$(basename $(cd $(dirname $BASH_SOURCE); pwd -P))
    @
    @function descend_into() {
    @    echo
    @    echo "********* $me : running $1 examples *********"
    @    echo
    @    cd $1
    @    ./run_all.sh
    @    cd ..
    @}
    @
    @function run_command() {
    @    echo
    @    echo "********* Running $me : component $1 *********"
    @    echo
    @    ./$1.sh
    @}
    @
END
    for d in $subdirs; do
        [[ $d = "*/" ]] && continue
        d=${d%/}
        [[ -d $d ]] || continue
        cd $d
        add_run_all_sh && echo descend_into '"'$d'"' >> ../run_all.sh
        cd ..
    done

    for f in $shfiles; do
        [[ -f $f ]] || continue
        echo run_command '"'$(basename $f .sh)'"' >> run_all.sh
    done

    chmod +x run_all.sh
}

add_run_all_bat
add_run_all_sh