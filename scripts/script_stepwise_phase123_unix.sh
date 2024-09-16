#!/bin/bash

# Check if no arguments are passed
if [ -z "$1" ]; then
    echo "Usage: $(basename "$0") \"<string_list>\""
    exit 1
fi

# Set default value for DATASET
if [ -z "$5" ]; then
    DATASET="HumanEvalComm"
else
    DATASET="$5"
fi

if [ -z "$6" ]; then
    PHASE1_PROMPT="prompt1"
else
    PHASE1_PROMPT="$6"
fi

# Split the string list into an array
string_of_strings="$1"
string_of_strings=${string_of_strings//\"/}

# Process each string in the list
for i in $string_of_strings; do
    if [ "$2" == "0" ]; then
        # Only for Okanagan, GPT 3.5 and GPT 4
        python generate_response.py -d "$DATASET" -m "$i" -n 1 -t 1 -o manualRemove -minp "$3" -maxp "$4" --log_phase_input 0 --log_phase_output 1 --phase1_prompt "$PHASE1_PROMPT"
    elif [ "$2" == "1" ]; then
        python generate_response.py -d HumanEvalComm -m "$i" -n 1 -t 1 -o manualRemove -minp "$3" -maxp "$4" --log_phase_input 1 --log_phase_output 2
    elif [ "$2" == "2" ]; then
        # Only for Okanagan, GPT 3.5 and GPT 4
        python generate_response.py -d HumanEvalComm -m "$i" -n 1 -t 1 -o manualRemove -minp "$3" -maxp "$4" --log_phase_input 2 --log_phase_output 3
    elif [ "$2" == "3" ]; then
        # Extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
        python intermedia_analyze.py -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_3 -n 1
    elif [ "$2" == "3-1" ]; then
        # Extract code and run test cases and other metrics for each problem. input: file in log/  output: file in log/record/
        python intermedia_analyze.py -f log/manualRemove_dataset_HumanEval_model_"$i"_topn_1_temperature_1.0.log_1 -n 1
    elif [ "$2" == "4" ]; then
        # Compute more metrics for each problem. input: file in ./log/record/ output: file in ./result_data/
        python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEvalComm -m "$i" -t 1 -o R1 -n 1 -s 3
    elif [ "$2" == "4-1" ]; then
        # Compute more metrics for each problem. input: file in ./log/record/ output: file in ./result_data/
        python syntactic_similarity_OER.py -e manualRemove_dataset_HumanEval -m "$i" -t 1 -o R1 -n 1 -s 1
    elif [ "$2" == "5" ]; then
        # Aggregate and display metrics for all problems
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
    elif [ "$2" == "5-1" ]; then
        # Aggregate and display metrics for all problems
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEval -m "$i" -t 1 -n 1
    elif [ "$2" == "6" ]; then
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt1a -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt1c -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt1p -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt2ac -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt2ap -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt2cp -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
        python measurement_summary_draw_heatmap.py -e manualRemove -d HumanEvalComm -m "$i" -t 1 -n 1 -pt prompt3acp -f log/manualRemove_dataset_HumanEvalComm_model_"$i"_topn_1_temperature_1.0.log_2
    fi
done
