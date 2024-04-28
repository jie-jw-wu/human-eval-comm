REM @echo off

REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat Meta-Llama-3-8B-Instruct CodeLlama-13b-Instruct-hf" 1 0 165
REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf CodeQwen1.5-7B-Chat" 1 0 165


REM Check if no arguments are passed
if %1=="" (
    echo Usage: %~nx0 "<string_list>"
    exit /b 1
)

REM Split the string list into an array
setlocal enabledelayedexpansion
REM %1 is: "cars plans others", %~1" is: cars plans others", (%~1) is: (cars plans others)

set "string_of_strings=%~1"
set "string_of_strings=!string_of_strings:"=!"

REM Split the string list into an array
for %%i in (!string_of_strings!) do (
    if "%2"=="0" (
        REM only for Okanagan, GPT 3.5 and GPT 4
        python generate_response.py -d HumanEvalComm -m %%i -n 1 -t 1 -o manualRemove -minp %3 -maxp %4 --log_phase_input 0 --log_phase_output 1
    ) else if "%2"=="1" (
        python generate_response.py -d HumanEvalComm -m %%i -n 1 -t 1 -o manualRemove -minp %3 -maxp %4 --log_phase_input 1 --log_phase_output 2
    ) else if "%2"=="2" (
        REM only for Okanagan, GPT 3.5 and GPT 4
        python generate_response.py -d HumanEvalComm -m %%i -n 1 -t 1 -o manualRemove -minp %3 -maxp %4 --log_phase_input 2 --log_phase_output 3
    ) else if "%2"=="3" (
        rem # extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
        python intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_3 -n 1
    ) else if "%2"=="4" (
        rem # compute more metrics for each problem, such as test pass rate, question quality rate, comm. rate, etc. input: file in ./log/record/ output: file in ./result_data/
        python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEvalComm -m %%i -t 1 -o R1 -n 1 -s 3
    ) else if "%2"=="5" (
        rem # aggregate and display metrics for all problems
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1
    ) else if "%2"=="6" (
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt1a
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt1c
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt1p
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt2ac
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt2ap
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt2cp
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt3acp
    )
)





endlocal
