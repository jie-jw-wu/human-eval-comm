#!/bin/bash
#SBATCH --time=5:30:00
#SBATCH --nodes=1
#SBATCH --gpus-per-node=a100:1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=107000M
#SBATCH --account=def-fard

module load python rust cuda arrow/17.0.0
source ~/ENV/bin/activate
cd $SLURM_SUBMIT_DIR
echo "we are in dir $SLURM_SUBMIT_DIR"


# command-line argument
MODEL=$1
FINETUNED_MODEL_PATH=$2
MODEL_NAME_OR_PATH=$3
MIN_P=$4
echo "MODEL is $MODEL"
echo "FINETUNED_MODEL_PATH is $FINETUNED_MODEL_PATH"
echo "MODEL_NAME_OR_PATH is $MODEL_NAME_OR_PATH"

python generate_response.py -d HumanEvalComm -m "$MODEL" -n 1 -t 1 -s 0 -o manualRemove -minp "$MIN_P$ --hf_dir /scratch/jie --model_name_or_path "$MODEL_NAME_OR_PATH" --finetuned_model_path "$FINETUNED_MODEL_PATH" -maxp -1 --seq_length 512 --log_phase_input 0 --log_phase_output 1 --use_int8

## below is the previous command that works
#python generate_response.py -d HumanEvalComm -m deepseek-coder-6.7b-instruct-finetuned-exp3 -n 1 -t 1 -s 0 -o manualRemove -minp 136 --hf_dir /scratch/jie --model_name_or_path /project/def-fard/jie/deepseek-ai/deepseek-coder-6.7b-instruct --finetuned_model_path /project/def-fard/jie/finetuned_models/deepseek-coder-6.7b-instruct-finetuned-exp3 -maxp -1 --seq_length 512 --log_phase_input 0 --log_phase_output 1 --use_int8
