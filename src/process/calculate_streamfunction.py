#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download a single year of 6-Hour Reanalysis V2 data from
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""

import argparse
import os
import xarray as xr
import numpy as np
import pandas as pd
from windspharm.xarray import VectorWind

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--uwnd", help="path to zonal wind file")
parser.add_argument("--vwnd", help="path to meridional wind file")

def calculate_streamfunction(uwnd, vwnd):
    """Calculate the Streamfunction
    """
    uwnd_ds = xr.open_dataarray(uwnd)
    vwnd_ds = xr.open_dataarray(vwnd)
    wind = VectorWind(uwnd_ds, vwnd_ds)
    psi = wind.streamfunction()
    return psi

def to_daily(hourly):
    """Convert data to daily time step
    """
    old_time = pd.to_datetime(hourly['time'].values)
    new_time = old_time + pd.DateOffset(hours=12) # OFFSET 12 HOURS
    hourly['time'] = new_time
    daily = hourly.resample(time='1D').mean(dim='time')
    return daily

def main():
    """Run everything
    """
    args = parser.parse_args()
    uwnd = os.path.abspath(args.uwnd)
    vwnd = os.path.abspath(args.vwnd)
    outfile = os.path.abspath(args.outfile)
    psi = calculate_streamfunction(uwnd, vwnd)
    longitudes = psi['lon'].values
    longitudes[np.where(longitudes > 180)] -= 360
    psi['lon'].values = longitudes
    psi = to_daily(psi)
    if os.path.isfile(outfile):
        os.remove(outfile)
    psi.to_netcdf(outfile, format='NETCDF4', mode='w')

if __name__ == "__main__":
    main()
