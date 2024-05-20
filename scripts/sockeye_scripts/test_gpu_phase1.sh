#!/bin/bash
 
#SBATCH --job-name=jw_phase1          
#SBATCH --account=st-fhendija-1-gpu    
#SBATCH --nodes=1                  
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8                          
#SBATCH --mem=44G                  
#SBATCH --time=10:00:00             
#SBATCH --gpus-per-node=3
#SBATCH --output=%x-%j.log         
#SBATCH --error=%x-%j.err         
#SBATCH --mail-user=jie.jw.wu@ubc.ca
#SBATCH --mail-type=ALL                               

echo "This job ran on $HOSTNAME"
cd $SLURM_SUBMIT_DIR
echo "we are in dir $SLURM_SUBMIT_DIR"
module restore jw-gpu
source ~/.bashrc
conda activate /arc/project/st-fhendija-1/jwu/jw-gpu
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo "Full JOB:"
python generate_response.py -d $3 -m $1 -n 1 -t 1 -s 0 -o manualRemove --hf_dir /scratch/st-fhendija-1/jwu/cache --model_name_or_path /arc/project/st-fhendija-1/jwu/$2 -maxp -1 --seq_length 512 --log_phase_input 0 --log_phase_output 1 --use_fp16
conda deactivate
