#!/bin/bash

#SBATCH --job-name=twentyfirst_aggregate
#SBATCH --mem=40G
#SBATCH --time=8:00:00
#SBATCH --mail-user=sallen@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --account=rrg-allen
# stdout and stderr file paths/names
#SBATCH --output=/scratch/allen/MIDOSS/aggregate/twentyfirst_stdout
#SBATCH --error=/scratch/allen/MIDOSS/aggregate/twentyfirst_stderr


module load python/3.8.2
source ~/venvs/jupyter/bin/activate

cd /scratch/allen/MIDOSS/aggregate

python3 -m Incremental_Sums twentieth_200 twentyfirst_200 /scratch/dlatorne/MIDOSS/runs/monte-carlo/21-200_near-BP_spill-hr_2021-12-16T222516 False
