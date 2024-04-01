#!/bin/bash

#SBATCH --job-name=fiftyfirst_aggregate
#SBATCH --mem=40G
#SBATCH --time=8:00:00
#SBATCH --mail-user=sallen@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --account=rrg-allen
# stdout and stderr file paths/names
#SBATCH --output=/scratch/allen/MIDOSS/aggregate/fiftyfirst_stdout
#SBATCH --error=/scratch/allen/MIDOSS/aggregate/fiftyfirst_stderr

RESULTS_DIR="/scratch/dlatorne/MIDOSS/runs/monte-carlo/51-10_near-BP_try3_2022-06-05T155341"

module load python/3.8.2
source ~/venvs/jupyter/bin/activate

cd /scratch/allen/MIDOSS/aggregate

python3 -m SaveBeaching ${RESULTS_DIR}/results/
python3 -m Incremental_Sums fiftieth_200 fiftyfirst_200 ${RESULTS_DIR} False

