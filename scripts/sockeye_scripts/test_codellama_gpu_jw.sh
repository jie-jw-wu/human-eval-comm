#!/bin/bash
 
#SBATCH --job-name=jw_codellama_test            
#SBATCH --account=st-fhendija-1-gpu    
#SBATCH --nodes=1                  
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12                           
#SBATCH --mem=64G                  
#SBATCH --time=12:00:00             
#SBATCH --gpus-per-node=4
#SBATCH --output=%x-%j.log         
#SBATCH --error=%x-%j.err         
#SBATCH --mail-user=jie.jw.wu@ubc.ca
#SBATCH --mail-type=ALL                               

echo "This job ran on $HOSTNAME"
cd $SLURM_SUBMIT_DIR
echo "we are in dir $SLURM_SUBMIT_DIR"
module restore jw-gpu
conda init bash
source ~/.bashrc
conda activate /arc/project/st-fhendija-1/jwu/jw-gpu
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo "JOB 1:"
python generate_response.py -d HumanEvalComm -m CodeLlama-7b-hf -n 1 -t 1 -s 0 -o manualRemove --hf_dir /scratch/st-fhendija-1/jwu/cache --model_name_or_path /arc/project/st-fhendija-1/jwu/codellama/CodeLlama-7b-hf -maxp -1 --seq_length 20 --do_test_only --user_input="def string_length(s):"
echo "JOB 2:"
python generate_response.py -d HumanEvalComm -m CodeLlama-7b-hf -n 1 -t 1 -s 0 -o manualRemove --hf_dir /scratch/st-fhendija-1/jwu/cache --model_name_or_path /arc/project/st-fhendija-1/jwu/codellama/CodeLlama-7b-hf -maxp -1 --seq_length 200 --do_test_only --user_input="You are an expert software developer who writes high quality code. With below information, please either generate Python3 code (Respond directly with code only with markdown), or ask clarifying questions: \nfrom typing import List\ndef candidate(...) -> bool:\n \"\"\" Check given a list of number.\"\"\"\n"
conda deactivate
