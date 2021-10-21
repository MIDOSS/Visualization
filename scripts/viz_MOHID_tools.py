"""Functions for processing MOHID output on Compute Canada machines
"""
import os
import pathlib
import yaml
import numpy
import xarray
from datetime import datetime
from glob import glob

def get_MOHID_netcdf_filenames(results_dir, output_dir):
    """Get lists of filepaths and filenames for netcdf files of model output, 
    grouped by oil types. NOTE: jet and gas are run as diesel; other is run 
    as bunker.  
    
    :param str results_dir: File path for root directory of run sets. 
    On Graham, the filepath is `/scratch/dlatorne/MIDOSS/runs/monte-carlo`
    
    :param str output_dir: File path for storing MOHID_results_locations_{date}.yaml,
    which contains file paths for completed runs, sorted by oil type.  
    
    :return: Dataframe of file paths and names, sorted by oil types, namely: 
    akns, bunker, dilbit, jet, diesel, gas and other.  Note: jet and gas are 
    run as diesel; other is run as bunker.  
    :rtype: :py:class:`pandas.DataFrame`
    """
    oil_types = [
        'akns', 
        'bunker', 
        'dilbit', 
        'jet', 
        'diesel', 
        'gas', 
        'other'
    ]
    # get list of runsets
    runsets = sorted(glob(os.path.join(results_dir,"near-BP_*")))
    # get list of runs within each runset
    runs = []
    for runset in runsets:
        runs.extend(sorted(
            glob(os.path.join(runset,'results','near-BP_*')))[:])        
    # get complete list of netcdf files
    netcdf_files = []
    for run in runs:
        netcdf_files.extend(sorted(
            glob(os.path.join(run,'Lagrangian*.nc')))[:])
    # sort filenames by oil type.  
    file_boolean = {}
    files = {}
    files['all'] = []
    for oil in oil_types:
        file_boolean[oil] = [oil in file for file in netcdf_files]
        files[oil]=[file for i,file in enumerate(netcdf_files) \
            if file_boolean[oil][i]]
        files['all'].extend(files[oil])
    
    # write filenames to .yaml with timestamp in filename
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H:%M:%S")
    out_f = output_dir+f'/MOHID_results_locations_{dt_string}.yaml'
    with open(out_f, 'w') as output_yaml:
        documents = yaml.safe_dump(files, output_yaml)
    
    return files

def aggregate_MOHID(run_list, surface_threshold=3e-3, beach_threshold=15e-3):
    """I still need to add a header here :-) """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # dimensions, constants, and dictionaries
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    nruns = len(run_list)
    ny,nx = 896, 396
    x, y = numpy.arange(0,nx), numpy.arange(0,ny) 
    # define time thresholds
    one_day = numpy.timedelta64(24,'h')
    three_days = numpy.timedelta64(48,'h')
    seven_days = numpy.timedelta64(168,'h')
    # Dictionary for organizing run information
    files=[]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Create xarrays for aggregating beaching presence
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    dims = ('nspills','grid_y','grid_x')
    MOHID_In = xarray.Dataset(
        data_vars = dict(
            BeachTime=(dims, numpy.zeros((nruns,ny,nx))),
            BeachVolume=(dims, numpy.zeros((nruns,ny,nx),dtype=float)),
            BeachPresence=(dims, numpy.zeros((nruns,ny,nx),dtype=int)),
            BeachPresence_one=(dims, numpy.zeros((nruns,ny,nx),dtype=int)),
            BeachPresence_three=(dims, numpy.zeros((nruns,ny,nx),dtype=int)),
            BeachPresence_seven=(dims, numpy.zeros((nruns,ny,nx),dtype=int))),
        coords=dict(
            grid_y=range(ny),
            grid_x=range(nx))
    )

    dims = ('grid_y','grid_x')
    Aggregate_Out = xarray.Dataset(
        data_vars = dict(
            MinBeachTime=(dims, numpy.zeros((ny,nx)),{"units":"hours"}), #An experiment with attributing variables
            TotalBeachVolume=(dims, numpy.zeros((ny,nx),dtype=float)),
            BeachPresence=(dims, numpy.zeros((ny,nx),dtype=int)),
            BeachPresence_one=(dims, numpy.zeros((ny,nx),dtype=int)),
            BeachPresence_three=(dims, numpy.zeros((ny,nx),dtype=int)),
            BeachPresence_seven=(dims, numpy.zeros((ny,nx),dtype=int))), 
        coords=dict(
            grid_y=range(ny),
            grid_x=range(nx)), 
        attrs=dict(
            MinBeachTime_units = "hours",
            MinBeachTime=("Earliest, non-zero beaching arrival time at locations " \
                "where beached oil is above BeachVolume_threshold"),
            TotalBeachVolume="Total volume beached over all runs where volume>BeachVolume_threshold in any given, individual run",
            TotalBeachVolume_units="meters-cubed",
            BeachVolume_threshold=beach_threshold,
            BeachVolume_threshold_units="meters-cubed",
            BeachPresence="Mask[0,1] where 1 indicates oil presence above BeachVolume_threshold",
            BeachPresence_one="Mask[0,1] where 1 indicates oil presence above BeachVolume_threshold and within the first 24 hours of spill",
            BeachPresence_three="Mask[0,1] where 1 indicates oil presence above BeachVolume_threshold and within the first 72 hours of spill",
            BeachPresence_seven="Mask[0,1] where 1 indicates oil presence above BeachVolume_threshold and within the first 168 hours of spill",

        )
    )
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # loop through runs and aggregate beaching information
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    for run in range(nruns):
        input_file = run_list[run]
        if os.path.isfile(input_file):
            files.append(input_file)
            with xarray.open_dataset(input_file) as ds:
                dt = ds.Beaching_Time-ds.Beaching_Time.min()
                # Beaching time (converted from ns to hours)
                MOHID_In.BeachTime[run,:,:]=dt*1e-9/3600
                # Set time to zero where volume is below threshold 
                MOHID_In['BeachTime'] = MOHID_In.BeachTime.where(
                    ds.Beaching_Volume>beach_threshold,
                    0 #if above is false
                )
                # Set all null values to 1 billion hours to get earliest arrival time
                MOHID_In['BeachTime'] = MOHID_In.BeachTime.where(
                    MOHID_In.BeachTime>0,
                    1e9
                )
                # Save volume over threshold 
                MOHID_In.BeachVolume[run,:,:] = ds.Beaching_Volume.where(
                    ds.Beaching_Volume>beach_threshold,
                    0
                )
                # Beaching presence masks
                dtmask = xarray.DataArray(
                    data=numpy.ones_like(ds.Beaching_Time, dtype=int),
                    coords=ds.Beaching_Time.coords,
                    dims=ds.Beaching_Time.dims,
                )       
                # Presence above threshold
                MOHID_In.BeachPresence[run,:,:] = dtmask.where(
                    ds.Beaching_Volume>beach_threshold, 
                    0
                )
                MOHID_In.BeachPresence_one[run,:,:] = dtmask.where(
                    numpy.logical_and(ds.Beaching_Volume>beach_threshold, dt<=one_day), 
                    0
                )  
                MOHID_In.BeachPresence_three[run,:,:] = dtmask.where(
                    numpy.logical_and(ds.Beaching_Volume>beach_threshold, dt<=three_days), 
                    0
                )
                MOHID_In.BeachPresence_seven[run,:,:] = dtmask.where(
                    numpy.logical_and(ds.Beaching_Volume>beach_threshold, dt<=seven_days), 
                    0
                )
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Flatten MOHID output into 2D arrays by 
    # taking minimum of spill values or adding across spill values 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Aggregate_Out['MinBeachTime'] = MOHID_In['BeachTime'].min(dim='nspills')
    Aggregate_Out['MinBeachTime'] = Aggregate_Out.MinBeachTime.where(
        Aggregate_Out.MinBeachTime<1e9,
        0
    )
    Aggregate_Out['TotalBeachVolume'] = MOHID_In['BeachVolume'].sum(dim='nspills')
    Aggregate_Out['BeachPresence'] = MOHID_In['BeachPresence'].sum(dim='nspills')
    Aggregate_Out['BeachPresence_one'] = MOHID_In['BeachPresence_one'].sum(dim='nspills')
    Aggregate_Out['BeachPresence_three'] = MOHID_In['BeachPresence_three'].sum(dim='nspills')
    Aggregate_Out['BeachPresence_seven'] = MOHID_In['BeachPresence_seven'].sum(dim='nspills')
    
    return MOHID_In, Aggregate_Out, files