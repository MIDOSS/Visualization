"""Functions for processing MOHID output on Compute Canada machines
"""
import os
import pathlib
import yaml
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