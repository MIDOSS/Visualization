#!/bin/bash

#SBATCH --job-name=eleventh_aggregate
#SBATCH --mem=40G
#SBATCH --time=8:00:00
#SBATCH --mail-user=sallen@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --account=rrg-allen
# stdout and stderr file paths/names
#SBATCH --output=/scratch/allen/MIDOSS/aggregate/eleventh_stdout
#SBATCH --error=/scratch/allen/MIDOSS/aggregate/eleventh_stderr


module load python/3.8.2
source ~/venvs/jupyter/bin/activate

cd /scratch/allen/MIDOSS/aggregate

python3 -m Incremental_Sums tenth_200 eleventh_200 /scratch/dlatorne/MIDOSS/runs/monte-carlo/11-200_near-BP_spill-hr_2021-12-14T172256 False
