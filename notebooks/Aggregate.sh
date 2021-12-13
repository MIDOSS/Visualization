#!/bin/bash

#SBATCH --job-name=eighth_aggregate
#SBATCH --mem=40G
#SBATCH --time=8:00:00
#SBATCH --mail-user=sallen@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --account=rrg-allen
# stdout and stderr file paths/names
#SBATCH --output=/scratch/allen/MIDOSS/aggregate/eighth_stdout
#SBATCH --error=/scratch/allen/MIDOSS/aggregate/eighth_stderr


module load python/3.8.2
source ~/venvs/jupyter/bin/activate

cd /scratch/allen/MIDOSS/aggregate

python3 -m Incremental_Sums seventh_200 eighth_200 /scratch/dlatorne/MIDOSS/runs/monte-carlo/8-200_near-BP_spill-hr_2021-12-12T131941 False
