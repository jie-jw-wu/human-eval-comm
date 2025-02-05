#!/bin/bash

# run this script under root folder

######################## DEFINE THESE VALUES########################
# step is {1,2,3} （When datset is HumanEvalComm） or {1,2} (When dataset is HumanEval)
# run this script when step is 1, 2, ... (sequentially with increasing step)
step=1
dataset="HumanEvalComm"
use_alliance=1
minp=110
maxp=165
step1_prompt="prompt1"
step2_prompt="prompt1"
# alliance arguments
MODEL="deepseek-coder-6.7b-instruct-finetuned-0202"
FINETUNED_MODEL_PATH="/project/def-fard/jie/finetuned_models/deepseek-coder-6.7b-instruct-finetuned-0202"
MODEL_NAME_OR_PATH="/project/def-fard/jie/deepseek-ai/deepseek-coder-6.7b-instruct"
# note sure if this is needed
export OPENAI_KEY=''
####################################################################

# script paths
SCRIPT_PATH="./scripts/script_stepwise_phase123_unix.sh"
ALLIANCE_SCRIPT_STEP1_PATH="./scripts/alliance_scripts/submit_evaluation_step_1.sh"
ALLIANCE_SCRIPT_STEP3_PATH="./scripts/alliance_scripts/submit_evaluation_step_3.sh"
phase=0

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: $SCRIPT_PATH not found."
    exit 1
fi

# Make the script executable
chmod +x "$SCRIPT_PATH"

# Execute the script
#Phase 0
#sbatch "$ALLIANCE_SCRIPT_PATH" "$MODEL" "$FINETUNED_MODEL_PATH" "$MODEL_NAME_OR_PATH"

run_humanevalcomm() {
    if [ "$step" -eq 1 ]; then
        if [ "$use_alliance" -eq 1 ]; then
            sbatch "$ALLIANCE_SCRIPT_STEP1_PATH" "$MODEL" "$FINETUNED_MODEL_PATH" "$MODEL_NAME_OR_PATH"
        elif [ "$use_alliance" -eq 0 ]; then
            phase=0
            "$SCRIPT_PATH" "$MODEL" "$phase" "$minp" "$maxp" "$dataset" "$step1_prompt"
        fi
    elif [ "$step" -eq 2 ]; then
        phase=1
        "$SCRIPT_PATH" "$MODEL" "$phase" "$minp" "$maxp" "$dataset" "$step2_prompt"
    elif [ "$step" -eq 3 ]; then
        phase=2
        if [ "$use_alliance" -eq 1 ]; then
            sbatch "$ALLIANCE_SCRIPT_STEP3_PATH" "$MODEL" "$FINETUNED_MODEL_PATH" "$MODEL_NAME_OR_PATH"
        elif [ "$use_alliance" -eq 0 ]; then
            "$SCRIPT_PATH" "$MODEL" "$phase" "$minp" "$maxp" "$dataset"
        fi
    elif [ "$step" -eq 4 ]; then
        "$SCRIPT_PATH" "$MODEL" 3 "$minp" "$maxp" "$dataset"
        "$SCRIPT_PATH" "$MODEL" 4 "$minp" "$maxp" "$dataset"
        "$SCRIPT_PATH" "$MODEL" 5 "$minp" "$maxp" "$dataset"
        "$SCRIPT_PATH" "$MODEL" 6 "$minp" "$maxp" "$dataset"
    else
        echo "Error: step must be 1, 2, 3 or 4."
        exit 1
    fi
}

run_humaneval() {
    if [ "$step" -eq 1 ]; then
        if [ "$use_alliance" -eq 1 ]; then
            sbatch "$ALLIANCE_SCRIPT_PATH" "$MODEL" "$FINETUNED_MODEL_PATH" "$MODEL_NAME_OR_PATH"
        elif [ "$use_alliance" -eq 0 ]; then
            phase=0
            "$SCRIPT_PATH" "$model" "$phase" "$minp" "$maxp" "$dataset" "$step1_prompt"
        fi
    elif [ "$step" -eq 2 ]; then
        "$SCRIPT_PATH" "$MODEL" 3-1 "$minp" "$maxp" "$dataset"
        "$SCRIPT_PATH" "$MODEL" 4-1 "$minp" "$maxp" "$dataset"
        "$SCRIPT_PATH" "$MODEL" 5-1 "$minp" "$maxp" "$dataset"
    else
        echo "Error: step must be 1, 2."
        exit 1
    fi
}

if [ "$dataset" == "HumanEvalComm" ]; then
    run_humanevalcomm
elif [ "$dataset" == "HumanEval" ]; then
    run_humaneval
else
    echo "Error: unknown dataset."
    exit 1
fi