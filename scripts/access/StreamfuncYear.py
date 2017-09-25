'''
Download the streamfunction for a specified year and level and save to file
Data from NCAR/NCEP Reanalysis I 6-hourly
'''

import numpy as np
import pandas as pd
import xarray as xr
from windspharm.xarray import VectorWind
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--level', type=int, nargs=1, help = 'Pressure level (hPa) for data')
parser.add_argument('--year', nargs=1, type=int, help='The year of data to download')
parser.add_argument('--outfile', nargs=1, help='The output file to save!')

def read_reanalysis2(url, level):
    import xarray as xr
    import numpy as np
    # reading in this data is a bit strange
    ds = xr.open_dataarray(url, decode_cf=False).sel(level=level)
    del ds.attrs['_FillValue']
    scale = ds.attrs['scale_factor']
    offset = ds.attrs['add_offset']
    ds.values = ds.values * scale + offset # this is not done automatically
    return(ds)

def main():
    # parse the arguments
    args = parser.parse_args()
    year = args.year[0]
    level = args.level[0]
    outfile = args.outfile[0]

    # Get the U and V wind
    url_u = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2/pressure/uwnd.{}.nc'.format(year)
    url_v = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2/pressure/vwnd.{}.nc'.format(year)
    U = read_reanalysis2(url_u, level=level)
    V = read_reanalysis2(url_v, level=level)

    # Get streamfunction
    W = VectorWind(U, V)
    streamfunc = W.streamfunction()

    # Save to file
    streamfunc.to_netcdf(outfile, format='NETCDF4')

if __name__ == '__main__':
    main()
