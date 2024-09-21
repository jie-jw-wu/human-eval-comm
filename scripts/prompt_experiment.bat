@echo off
setlocal enabledelayedexpansion

REM Variables for minp and maxp
set "minp=0"
set "maxp=1"

REM Check if both arguments are provided
if "%~2"=="" (
    echo Usage: %0 ^<phase1_prompt^> ^<phase2_prompt^>
    exit /b 1
)

set "phase1_prompt=%~1"
set "phase2_prompt=%~2"

REM Extract numbers from prompts and create model_postfix
set "phase1_num=%phase1_prompt:prompt=%"
set "phase2_num=%phase2_prompt:prompt=%"
set "model_postfix=_prompt%phase1_num%-%phase2_num%"

REM Define the function to create a string of postfixed model names
goto :main
:get_postfixed_models
    set "postfixed_models="
    for %%m in (%*) do (
        if defined postfixed_models (
            set "postfixed_models=!postfixed_models! %%m%model_postfix%"
        ) else (
            set "postfixed_models=%%m%model_postfix%"
        )
    )
    exit /b

:main
echo Phase 0
set "models=gpt-3.5-turbo-0125 Okanagan"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 0 %minp% %maxp% HumanEvalComm %phase1_prompt%
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 0 %minp% %maxp% HumanEvalComm %phase1_prompt%

call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 0 %minp% %maxp% HumanEval %phase1_prompt%
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 0 %minp% %maxp% HumanEval %phase1_prompt%

echo Phase 1
set "models=gpt-3.5-turbo-0125 Okanagan"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 1 %minp% %maxp% %phase2_prompt%
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 1 %minp% %maxp% %phase2_prompt%

echo Phase 2
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 2 %minp% %maxp%
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 2 %minp% %maxp%

echo Phase 3
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 3
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 3

echo Phase 4
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 4
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 4

echo Phase 3-1
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 3-1
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 3-1

echo Phase 4-1
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 4-1
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 4-1

echo Phase 5
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 5
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 5

echo Phase 6
set "models=gpt-3.5-turbo-0125"
call :get_postfixed_models %models%
echo call scripts\script_stepwise_phase123.bat "%postfixed_models%" 6
call scripts\script_stepwise_phase123.bat "%postfixed_models%" 6

endlocal