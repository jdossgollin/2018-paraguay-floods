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
from datetime import datetime

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--year", help="the year of data to download")
parser.add_argument("--X0", help="lon min")
parser.add_argument("--X1", help="lon max")
parser.add_argument("--Y0", help="lat min")
parser.add_argument("--Y1", help="lat max")

def download_data(outfile, year, lonmin, lonmax, latmin, latmax):
    # Get the URL
    url = 'http://iridl.ldeo.columbia.edu/home/.mbell/.ECMWF/.S2Stest/.S2S/.ECMF_ph2/'
    url += '.forecast/.perturbed/.sfc_precip/.tp/'
    url += 'X/{}/{}/RANGEEDGES/'.format(lonmin, lonmax)
    url += 'Y/{}/{}/RANGEEDGES/'.format(latmin, latmax)
    url += '[X+Y]average/'
    url += 'L+differences/'
    url += 'dods'

    sdate = datetime(year, 9, 1)
    edate = datetime(year+1, 2, 29)

    # Load the data
    data = xr.open_dataarray(url)
    data = data.sel(S=slice(sdate, edate))
    data['S'] = pd.to_datetime(data['S'].values)
    data['L'] = data['L']
    if os.path.isfile(outfile):
        os.remove(outfile)
    data.to_netcdf(outfile, format='NETCDF4', mode='w')

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    lonmin = args.X0
    lonmax = args.X1
    latmin = args.Y0
    latmax = args.Y1
    year = int(args.year)

    download_data(
        outfile=outfile,
        lonmin=lonmin, lonmax=lonmax,
        latmin=latmin, latmax=latmax,
        year=year
    )

if __name__ == "__main__":
    main()
