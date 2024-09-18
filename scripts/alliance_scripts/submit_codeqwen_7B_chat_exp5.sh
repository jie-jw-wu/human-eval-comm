#!/bin/bash
#SBATCH --time=5:00:00
#SBATCH --nodes=1
#SBATCH --gpus-per-node=a100:1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=107000M
#SBATCH --account=def-fard

module load python rust cuda arrow/17.0.0
source ~/ENV/bin/activate
cd $SLURM_SUBMIT_DIR
echo "we are in dir $SLURM_SUBMIT_DIR"
python generate_response.py -d HumanEvalComm -m CodeQwen1.5-7B-Chat-finetuned-v5 -n 1 -t 1 -s 0 -o manualRemove -minp 136 --hf_dir /scratch/jie --model_name_or_path /project/def-fard/jie/Qwen/CodeQwen1.5-7B-Chat --finetuned_model_path /project/def-fard/jie/finetuned_models/CodeQwen1.5-7B-Chat-finetuned-v5 -maxp -1 --seq_length 512 --log_phase_input 0 --log_phase_output 1 --use_int8
