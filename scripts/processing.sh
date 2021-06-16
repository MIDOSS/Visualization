#!/bin/bash

# Paths
results_path=/scratch/dlatorne/MIDOSS/runs/monte-carlo
save_path=/scratch/bmoorema/Results

# Run sets
runsets=(
    northern_strait_first30
    north_strait_2nd60
    north_strait_3rd150
    north_strait_4th122
    north_strait_5th362
)
timestamps=(
    2021-06-11T202428
    2021-06-12T141330
    2021-06-12T201317
    2021-06-13T143859
    2021-06-14T150753
)
nruns=(30 60 150 122 362)

# Loop through runsets
for i in "${!runsets[@]}"; do

    # Loop through runs
    for ((run=0;run<nruns[i];run++)); do

	# Break if hdf5_2_nc processing hasn't commenced
	if [[ $run -gt 268 ]]; then
	    break
	fi
	
	# Define run directory
	rundir=${results_path}/${runsets[i]}_${timestamps[i]}/results/${runsets[i]}-${run}

	# Parse oiltype
	oiltype=(${rundir}/Lagrangian*.dat)
	oiltype=${oiltype##*/}
	oiltype=${oiltype##*_}
	oiltype=${oiltype%%-*}

	# Define filenames
	filename=Lagrangian_${oiltype}-${run}_${runsets[i]}-${run}

	# Loop through averaging periods
	for days in {1..7}; do

	    # Paths
	    tt_path=${save_path}/temp/${filename}_tt${days}d.nc
	    #pa_path=${save_path}/temp/${filename}_pa${days}d.nc
	    
	    # Compute time average
	    ncra --op_typ=ttl -d time,,$((24*$days)) -v OilWaterColumnOilVol_3D ${rundir}/${filename}.nc ${tt_path}

	    # Determine presence/absence
	    #ncap2 -S ./ncap2_pa.nco ${tt_path} ${pa_path}
	    
	done
    done
    echo "Done processing $((1+$i))/5: ${runsets[i]}"
done
