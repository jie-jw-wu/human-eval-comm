REM @echo off

REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat Meta-Llama-3-8B-Instruct CodeLlama-13b-Instruct-hf" 1 0 165
REM run phase 1: ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 0 0 5 HumanEval
REM run phase 2: ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf CodeQwen1.5-7B-Chat" 1 0 165
REM run phase 3: 
REM analyze remaining open models:
    REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 3
    REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 4
    REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 5
    REM ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf" 6
REM run original problem without modification:
    REM ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 0 0 165 HumanEval
    REM ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 3-1 0 165 HumanEval
    REM ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 4-1 0 165 HumanEval
    REM ./scripts/script_stepwise_phase123.bat "gpt-3.5-turbo-0125 Okanagan" 5-1 0 165 HumanEval
REM phase 5: ./scripts/script_stepwise_phase123.bat "deepseek-coder-6.7b-instruct deepseek-llm-7b-chat CodeQwen1.5-7B-Chat CodeLlama-13b-Instruct-hf CodeLlama-7b-Instruct-hf gpt-3.5-turbo-0125 Okanagan" 5

REM Check if no arguments are passed
if %1=="" (
    echo Usage: %~nx0 "<string_list>"
    exit /b 1
)
REM Check if %5 is empty
if "%~5"=="" (
    REM Set default value for %5
    set "DATASET=HumanEvalComm"
) else (
    REM %5 has a value
    set "DATASET=%~5"
)

REM Check if %6 is empty
if "%~6"=="" (
    REM Set default value for %6
    set "PHASE1_PROMPT=prompt1"
) else (
    REM %5 has a value
    set "PHASE1_PROMPT=%~6"
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
        python generate_response.py -d %DATASET% -m %%i -n 1 -t 1 -o manualRemove -minp %3 -maxp %4 --log_phase_input 0 --log_phase_output 1 --phase1_prompt %PHASE1_PROMPT%

    ) else if "%2"=="1" (
        python generate_response.py -d HumanEvalComm -m %%i -n 1 -t 1 -o manualRemove -minp %3 -maxp %4 --log_phase_input 1 --log_phase_output 2 --phase2_prompt %5
    ) else if "%2"=="2" (
        REM only for Okanagan, GPT 3.5 and GPT 4
        python generate_response.py -d HumanEvalComm -m %%i -n 1 -t 1 -o manualRemove -minp %3 -maxp %4 --log_phase_input 2 --log_phase_output 3
    ) else if "%2"=="3" (
        rem # extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
        python intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_3 -n 1
    ) else if "%2"=="3-1" (
        rem # extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
        python intermedia_analyze.py -f log/manualRemove_dataset_HumanEval_model_%%i_topn_1_temperature_1.0.log_1 -n 1
    ) else if "%2"=="4" (
        rem # compute more metrics for each problem, such as test pass rate, question quality rate, comm. rate, etc. input: file in ./log/record/ output: file in ./result_data/
        python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEvalComm -m %%i -t 1 -o R1 -n 1 -s 3
    ) else if "%2"=="4-1" (
        rem # compute more metrics for each problem, such as test pass rate, question quality rate, comm. rate, etc. input: file in ./log/record/ output: file in ./result_data/
        python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEval -m %%i -t 1 -o R1 -n 1 -s 1
    ) else if "%2"=="5" (
        rem # aggregate and display metrics for all problems
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
    ) else if "%2"=="5-1" (
        rem # aggregate and display metrics for all problems
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEval -m %%i -t 1 -n 1
    ) else if "%2"=="6" (
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt1a -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt1c -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt1p -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt2ac -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt2ap -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt2cp -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m %%i -t 1 -n 1 -pt prompt3acp -f log/manualRemove_dataset_HumanEvalComm_model_%%i_topn_1_temperature_1.0.log_2
    )
)





endlocal
