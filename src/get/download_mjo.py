#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download raw MJO data from
http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt
and parse it
"""

import argparse
import os
from datetime import datetime
import pandas as pd
import xarray as xr

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--syear", help="the first year to retain")
parser.add_argument("--eyear", help="the last year to retain")
parser.add_argument("--outfile", help="the path to the raw MJO data")
parser.add_argument("--infile", help="the filename of the data to save")

def download_data(sdate, edate, infile, outfile):
    """Download the MJO data"""
    col_names = ['year', 'month', 'day', 'RMM1', 'RMM2', 'phase', 'amplitude', 'source']
    mjo_df = pd.read_table(
        infile, delim_whitespace=True, index_col=None,
        skiprows=2, names=col_names
    )
    mjo_df['time'] = pd.to_datetime(mjo_df[['year', 'month', 'day']])
    mjo_df.set_index('time', inplace=True)
    mjo_df = mjo_df[['RMM1', 'RMM2', 'phase', 'amplitude']]
    mjo_df = mjo_df.loc[sdate:edate]
    mjo_ds = mjo_df.to_xarray()

    # save to file
    if os.path.isfile(outfile):
        os.remove(outfile)
    mjo_ds.to_netcdf(outfile, format='NETCDF4', mode='w')

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    infile = os.path.abspath(args.infile)
    sdate = datetime(int(args.syear), 1, 1)
    edate = datetime(int(args.eyear), 12, 31)
    download_data(sdate=sdate, edate=edate, infile=infile, outfile=outfile)

if __name__ == "__main__":
    main()
