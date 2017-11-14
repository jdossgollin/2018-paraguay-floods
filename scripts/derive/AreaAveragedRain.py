"""
GetRioPYRain
------------------

This script takes the area-averaged rainfall and saves to csv

"""

import xarray as xr
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--infile', nargs=1, help='the input file to read from')
parser.add_argument('--lonlim', nargs=2, type=float, help='the input file to read to')
parser.add_argument('--latlim', nargs=2, type=float, help='the input file to read to')
parser.add_argument('--outfile', nargs=1, help='the output file to save to')
args = parser.parse_args()

def main():
    infile = args.infile[0]
    outfile = args.outfile[0]
    latmin, latmax = np.min(args.latlim), np.max(args.latlim)
    lonmin, lonmax = np.min(args.lonlim), np.max(args.lonlim)
    rain = xr.open_dataset(infile).sel(lon = slice(lonmin, lonmax), lat = slice(latmin, latmax))
    rain_mean = rain.mean(dim=['lon', 'lat'])
    print(rain_mean)

    # Save to file
    rain_mean.to_netcdf(outfile)

if __name__ == '__main__':
    main()
