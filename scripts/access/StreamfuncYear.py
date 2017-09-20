'''
Download the streamfunction for a specified year and level and save to file
Data from NCAR/NCEP Reanalysis I 6-hourly
'''

import numpy as np
import xarray as xr
import os
from paraguayfloodspy.pars  import GetPars
from windspharm.xarray import VectorWind
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--level', type=int, nargs=1, help = 'Pressure level (hPa) for data')
parser.add_argument('--year', nargs=1, type=int, help='The year of data to download')
parser.add_argument('--outfile', nargs=1, help='The output file to save!')

def main():
    # parse the arguments
    args = parser.parse_args()
    year = args.year[0]
    level = args.level[0]
    outfile = args.outfile[0]

    # Get the U and V wind
    url_u = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/pressure/uwnd.{}.nc'.format(year)
    url_v = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/pressure/vwnd.{}.nc'.format(year)
    U = xr.open_dataarray(url_u).sel(level=level).load()
    V = xr.open_dataarray(url_v).sel(level=level).load()

    # Get streamfunction
    W = VectorWind(U, V)
    streamfunc = W.streamfunction()

    # Save to file
    streamfunc.to_netcdf(outfile, format='NETCDF4')

if __name__ == '__main__':
    main()
