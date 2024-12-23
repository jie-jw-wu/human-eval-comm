#!/bin/bash
 
#SBATCH --job-name="hello_world_echo_jw"
#SBATCH --account=st-fhendija-1
#SBATCH -t 00:01:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=%x-%j.log
#SBATCH --mail-user=jie.jw.wu@ubc.ca
 
cd $SLURM_SUBMIT_DIR
 
module load gcc/9.1.0
 
echo "This job ran on $HOSTNAME"
