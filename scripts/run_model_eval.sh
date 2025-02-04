#!/bin/bash

# run this script under root folder

######################## DEFINE THESE VALUES########################
model=""
phase=0
minp=0
maxp=165
phase1_prompt="prompt1"
phase2_prompt="prompt1"
use_alliance=1
# alliance arguments
MODEL="deepseek-coder-6.7b-instruct-finetuned-0202"
FINETUNED_MODEL_PATH="/project/def-fard/jie/finetuned_models/deepseek-coder-6.7b-instruct-finetuned-0202"
MODEL_NAME_OR_PATH="/project/def-fard/jie/deepseek-ai/deepseek-coder-6.7b-instruct"
####################################################################

# script paths
SCRIPT_PATH="./scripts/script_stepwise_phase123_unix.sh"
ALLIANCE_SCRIPT_PATH="./scripts/alliance_scripts/submit_evaluation_step_0.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: $SCRIPT_PATH not found."
    exit 1
fi

# Make the script executable
chmod +x "$SCRIPT_PATH"

# Execute the script
#Phase 0
sbatch "$ALLIANCE_SCRIPT_PATH" "$MODEL" "$FINETUNED_MODEL_PATH" "$MODEL_NAME_OR_PATH"
#"$SCRIPT_PATH" "$model" "$phase" "$minp" "$maxp" "$phase1_prompt"
