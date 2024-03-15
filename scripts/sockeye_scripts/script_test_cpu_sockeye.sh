#!/bin/bash
#SBATCH --time=0:01:00                    # Request 1 minute of runtime
#SBATCH --account=st-fhendija-1            # Specify your allocation code
#SBATCH --job-name=jw_job_array         # Specify the job name
#SBATCH --nodes=1                       # Defines the number of nodes for each sub-job.
#SBATCH --ntasks-per-node=1             # Defines tasks per node for each sub-job.
#SBATCH --mem=8G                        # Request 8 GB of memory    
#SBATCH --output=array_%A_%a.out        # Redirects standard output to unique files for each sub-job.
#SBATCH --error=array_%A_%a.err         # Redirects standard error to unique files for each sub-job.
#SBATCH --mail-user=jie.jw.wu@ubc.ca   # Email address for job notifications
#SBATCH --mail-type=ALL                 # Receive email notifications for all job events
    

cd $SLURM_SUBMIT_DIR

# Load all the software modules
module load python

# Your job array commands go here
echo "JW: This is a job array sub-job with index value $SLURM_ARRAY_TASK_ID"
echo "current dir: $SLURM_SUBMIT_DIR"
python generate_response.py -d HumanEvalComm -m OpenSourceModel -n 1 -t 1 -s 0 -o manualRemove --hf_dir D:\Study\Research\Projects\huggingface --model_name_or_path bigcode/starcoderbase-1b -maxp 1
