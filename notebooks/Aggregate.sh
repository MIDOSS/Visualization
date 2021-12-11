#!/bin/bash

#SBATCH --job-name=first_aggregate
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --mail-user=sallen@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --account=rrg-allen
# stdout and stderr file paths/names
#SBATCH --output=/scratch/allen/MIDOSS/aggregate/first_stdout
#SBATCH --error=/scratch/allen/MIDOSS/aggregate/first_stderr


module load python/3.8.2
source ~/venvs/jupyter/bin/activate

cd /scratch/allen/MIDOSS/aggregate

python3 -m Incremental_Sums nomatter first_200 /scratch/dlatorne/MIDOSS/runs/monte-carlo/1-200_near-BP_spill-hr_2021-12-09T134911 True



