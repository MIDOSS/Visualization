"""Module to Incrementally Sum MOHID results
"""
import numpy as np
import pandas as pd
from pathlib import Path
from os import fspath
import sys
import xarray as xr

oil_dict = {
            'akns': ['AKNS Spills', ['akns']],
            'bunker': ['Bunker and Other Spills', ['bunker', 'other']],
            'diesel': ['Diesel, Gas and Jet Spills', ['diesel', 'gas', 'jet']],
            'dilbit' : ['Dilbit Spills', ['dilbit']]
            }


def initialize(oiltype, mcsize=49, nsize=896, esize=396):

    beaching_time = np.zeros((mcsize+1, nsize, esize))
    beachpresence = np.zeros((nsize, esize))
    beaching_oil = np.zeros((mcsize+1, nsize, esize))
    oiling_time = np.zeros((mcsize+1, nsize, esize))
    oilpresence = np.zeros((nsize, esize))
    surface_oil = np.zeros((mcsize+1, nsize, esize))
    deeppresence = np.zeros((nsize, esize))
    deep_oil = np.zeros((mcsize+1, nsize, esize))
    deep_location = np.zeros((mcsize+1, nsize, esize))
    files_aggregate = pd.Series(data=['empty']*10000)
    count = 0

    coords = dict(grid_x=(["grid_x"], np.arange(esize)),
             grid_y=(["grid_y"], np.arange(nsize)),
             filecount=(["nf"], np.arange(10000)), )

    data_vars = dict(
        beaching_time=(["c", "grid_y", "grid_x"], beaching_time),
        beachpresence=(["grid_y", "grid_x"], beachpresence),
        beaching_oil=(["c", "grid_y", "grid_x"], beaching_oil),
        oiling_time=(["c", "grid_y", "grid_x"], oiling_time),
        oilpresence=(["grid_y", "grid_x"], oilpresence),
        surface_oil=(["c", "grid_y", "grid_x"], surface_oil),
        deeppresence=(["grid_y", "grid_x"], deeppresence),
        deep_oil=(["c", "grid_y", "grid_x"], deep_oil),
        deep_location=(["c", "grid_y", "grid_x"], deep_oil),
        files_aggregate=(["nf"], files_aggregate),
        nofiles = ([], 0)   )

    ds = xr.Dataset(data_vars=data_vars, coords=coords, attrs=dict(description=oiltype))

    return ds


def read_aggregate(oiltype, filename):
    ds = xr.open_dataset(f'{filename}_{oiltype}.nc')

    return ds


def write_aggregate(oiltype, filename, ds):
    ds.to_netcdf(f'{filename}_{oiltype}.nc')

    return

    
def readfile_aggregate(filename, depths, rng, specific, oils, mcsize=49, minoil=5, minSurf=3):
    pois = np.ones(mcsize+1)
    eps = 1e-7
    with xr.open_dataset(filename) as data:
        print (data.dims['time'])
        specific['nofiles'] = specific.nofiles + 1
        oils['nofiles'] = oils.nofiles + 1
        pois[1:] = rng.poisson(1, mcsize)
        
        beached = data.Beaching_Volume > minoil/1000.
        
        beachtime = (np.array(data.Beaching_Time - data.Beaching_Time.min())
              ) /  np.timedelta64(1, 's') /3600./24. * beached
        beach_oil = np.log(data.Beaching_Volume + eps) * beached
        
        specific['beachpresence'][:] = specific.beachpresence[:] + beached[:, :]
        oils['beachpresence'] = oils.beachpresence + beached
        specific['beaching_time'] = specific.beaching_time + (np.broadcast_to(beachtime, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose())
        oils['beaching_time'] = oils.beaching_time + (np.broadcast_to(beachtime, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
        specific['beaching_oil'] = specific.beaching_oil + (np.broadcast_to(beach_oil, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
        oils['beaching_oil'] = oils.beaching_oil + (np.broadcast_to(beach_oil, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
        
        oiled = data.OilWaterColumnOilVol_3D[:, 39].max(axis=0) > minSurf/1000.
        
        oiltime = (np.array(data.Oil_Arrival_Time - data.Oil_Arrival_Time.min())
              ) /  np.timedelta64(1, 's') /3600./24. * oiled
        oil_vol = np.log(data.OilWaterColumnOilVol_3D[:, 39].sum(axis=0) + eps) * oiled 
        
        specific['oilpresence'] = specific.oilpresence + oiled
        oils['oilpresence'] = oils.oilpresence + oiled
        specific['oiling_time'] = specific.oiling_time + (np.broadcast_to(oiltime, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose())
        oils['oiling_time'] = oils.oiling_time + (np.broadcast_to(oiltime, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose())
        specific['surface_oil'] = specific.surface_oil + (np.broadcast_to(oil_vol, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
        oils['surface_oil'] = specific.surface_oil + (np.broadcast_to(oil_vol, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
        
        specific['files_aggregate'][specific.nofiles-1] = fspath(filename)
        oils['files_aggregate'][oils.nofiles-1] = fspath(filename)
        print (specific.nofiles.values, oils.nofiles.values)
        
        zmax = 0
        
        water_column_oil = data.OilWaterColumnOilVol_3D[:, zmax:39].sum(axis=0)        
        print (water_column_oil.shape)
        data.close()   # yes, this should happen anyway...
    oiled = water_column_oil.max(axis=0) > minSurf/1000.
    column_oil = water_column_oil.sum(axis=0) + eps
    oil_vol = np.log(column_oil) * oiled
    
    specific['deeppresence'] = specific.deeppresence + oiled
    oils['deeppresence'] = oils.deeppresence + oiled
    specific['deep_oil'] = specific.deep_oil + (np.broadcast_to(oil_vol, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
    oils['deep_oil'] = specific.deep_oil + (np.broadcast_to(oil_vol, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
    print(oiled.sum())
    
    location = (depths[zmax:39] * water_column_oil.transpose()).transpose().sum(axis=0) * oiled / column_oil  
    specific['deep_location'] = specific.deep_location + (np.broadcast_to(location, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose()) 
    oils['deep_location'] = specific.deep_location + (np.broadcast_to(location, (mcsize+1, 896, 396)) 
                                                 * np.broadcast_to(pois, (396, 896, mcsize+1)).transpose())
        
        
        
    return specific, oils


def aggregate_a_directory(directory, init_files, infile, outfile):
        
    mesh = xr.open_dataset('~/MEOPAR/grid/mesh_mask201702.nc')
    depths = np.flip(np.array(mesh.gdept_1d[0]))
    mesh.close()

    rng = np.random.default_rng()

    mypath = Path(directory)

    if init_files:
        oils = initialize("All Spills")
    else:
        oils = read_aggregate('oils', infile)
        
    for oil_type in ['akns', 'bunker', 'diesel', 'dilbit']:
        print (oil_type)
        if init_files:
            specific = initialize(oil_dict[oil_type][0])
        else:
            specific = read_aggregate(oil_type, infile)
        for model_oil in oil_dict[oil_type][1]:
            print (model_oil)
            for filename in mypath.glob(f'results/*/Lagrangian*{model_oil}*.nc'):
                specific, oils = readfile_aggregate(filename, depths, rng, specific, oils)

        write_aggregate(oil_type, outfile, specific)
        specific.close()
        write_aggregate('oils_save', outfile, oils)

    write_aggregate('oils', outfile, oils)

    return
                

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    directory = sys.argv[3]
    init_files = False
    print (sys.argv[4], 'True')
    if len(sys.argv) == 5:
        if sys.argv[4] == 'True':
            init_files = True
    aggregate_a_directory(directory, init_files, infile, outfile)
