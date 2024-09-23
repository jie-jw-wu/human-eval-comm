#!/bin/bash

# Editable variables for minp and maxp
minp=1
maxp=165

# Check if both arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <phase1_prompt> <phase2_prompt>"
    exit 1
fi

phase1_prompt=$1
phase2_prompt=$2

# Extract numbers from prompts and create model_postfix
phase1_num=$(echo $phase1_prompt | sed 's/prompt//')
phase2_num=$(echo $phase2_prompt | sed 's/prompt//')
model_postfix="_prompt${phase1_num}-${phase2_num}"

# Function to create a string of postfixed model names
get_postfixed_models() {
    local models=("$@")
    local postfixed_models=""
    for model in "${models[@]}"; do
        postfixed_models+="${model}${model_postfix} "
    done
    echo $postfixed_models
}

#########################                              Phase 0
models=(
    "Okanagan"
    )
postfixed_models=$(get_postfixed_models "${models[@]}")
#./scripts/script_stepwise_phase123_unix.sh $postfixed_models 0 $minp $maxp HumanEvalComm $phase1_prompt

#./scripts/script_stepwise_phase123_unix.sh $postfixed_models 0 $minp $maxp HumanEval $phase1_prompt

#########################                              Phase 1
#./scripts/script_stepwise_phase123_unix.sh $postfixed_models 1 $minp $maxp $phase2_prompt

#########################                              Phase 2
#./scripts/script_stepwise_phase123_unix.sh $postfixed_models 2 $minp $maxp

#########################                              Phase 3
./scripts/script_stepwise_phase123_unix.sh $postfixed_models 3

#########################                              Phase 4
./scripts/script_stepwise_phase123_unix.sh $postfixed_models 4

#########################                              Phase 3-1
./scripts/script_stepwise_phase123_unix.sh $postfixed_models 3-1

#########################                              Phase 4-1
./scripts/script_stepwise_phase123_unix.sh $postfixed_models 4-1

#########################                              Phase 5
./scripts/script_stepwise_phase123_unix.sh $postfixed_models 5

#########################                              Phase 6
./scripts/script_stepwise_phase123_unix.sh $postfixed_models 6