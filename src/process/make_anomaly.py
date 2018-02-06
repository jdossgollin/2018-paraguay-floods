#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Take a list of data files, subset them, and calculate anomalies
"""

import argparse
import os
from glob import glob
import calendar
import xarray as xr
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--path", help="the files to read in")
parser.add_argument("--syear", type=int, help="start year")
parser.add_argument("--eyear", type=int, help="end year")
parser.add_argument("--X0", type=float)
parser.add_argument("--X1", type=float)
parser.add_argument("--Y0", type=float)
parser.add_argument("--Y1", type=float)

def read_netcdfs(files, dim, transform_func=None):
    """From http://xarray.pydata.org/en/stable/io.html#netcdf
    """
    def process_one_path(path):
        """Helper
        """
        with xr.open_dataset(path) as ds:
            if transform_func is not None:
                ds = transform_func(ds)
            ds.load()
            return ds

    paths = sorted(glob(files))
    datasets = [process_one_path(p) for p in paths]
    combined = xr.concat(datasets, dim)
    return combined

def calc_anomaly(path, outfile, syear, eyear, lonmin, lonmax, latmin, latmax):
    """Decompose into anomaly and subset geographically
    """
    # Read in the data
    def subset_function(ds):
        # HARD-CODED FOR NOW: subset NDJF, calculate "adjusted year"
        sub = ds.sortby('lon').sortby('lat').sortby('time').sel(
            lon=slice(lonmin, lonmax),
            lat=slice(latmin, latmax)
        )
        sub = sub.sel(time=np.in1d(sub['time.month'], np.array([11, 12, 1, 2])))
        return sub

    raw = read_netcdfs(path, dim='time', transform_func=subset_function)
    varname = list(raw.data_vars.keys())[0]
    raw = raw[varname]
    year = raw['time.year']
    month = raw['time.month']
    year_adj = year
    year_adj[np.in1d(month, [11, 12])] += 1
    raw.coords['year_adj'] = year_adj

    # Sub-set by date
    sdate = pd.Timestamp('{}-11-01'.format(syear))
    if calendar.isleap(eyear):
        edate = pd.Timestamp('{}-02-29'.format(eyear))
    else:
        edate = pd.Timestamp('{}-02-28'.format(eyear))
    raw = raw.sel(time=slice(sdate, edate)).load()

    # Get the data set
    anomaly = raw - raw.mean(dim='time')
    combined = xr.Dataset({'raw': raw, 'anomaly': anomaly})
    if os.path.isfile(outfile):
        os.remove(outfile)
    combined.to_netcdf(outfile, format='NETCDF4')

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    calc_anomaly(
        path=args.path,
        outfile=os.path.abspath(args.outfile),
        syear=int(args.syear),
        eyear=int(args.eyear),
        lonmin=args.X0,
        lonmax=args.X1,
        latmin=args.Y0,
        latmax=args.Y1
    )

if __name__ == "__main__":
    main()
