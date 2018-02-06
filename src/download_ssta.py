#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download monthly sea surface temperature anomalies from
http://iridl.ldeo.columbia.edu/expert/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/.Reyn_SmithOIv2/.monthly/.ssta/dods
"""

import argparse
import os
import xarray as xr
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")

def download_data(outfile):
    """Download the monthly SST anomaly data
    Args:
        outfile: the name of the file to save to
    """
    # read in the data
    url = 'http://iridl.ldeo.columbia.edu/expert/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/'
    url += '.Reyn_SmithOIv2/.monthly/.ssta/dods' # split lines
    data = xr.open_dataarray(url, decode_times=False) # doesn't follow time conventions

    # parse the time manually
    time = np.int_(np.floor(data['T']))
    year = 1960 + time // 12
    month = 1 + time % 12
    time = pd.to_datetime(year * 10000 + month * 100 + 1, format="%Y%m%d")
    data['T'] = time
    data.rename({'T': 'time'})

    # save to file
    if os.path.isfile(outfile):
        os.remove(outfile)
    data.to_netcdf(outfile, format='NETCDF4', mode='w')

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    download_data(outfile=outfile)

if __name__ == "__main__":
    main()
