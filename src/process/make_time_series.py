#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Get a time series averaged over some area
"""

import argparse
import os
import xarray as xr

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--infile", help="the input data")
parser.add_argument("--X0", type=float, help="lon min")
parser.add_argument("--X1", type=float, help="lon max")
parser.add_argument("--Y0", type=float, help="lat min")
parser.add_argument("--Y1", type=float, help="lat max")

def make_subset(infile, outfile, lonmin, lonmax, latmin, latmax):
    """Carry out the subsetting
    """
    # Read in the data
    data = xr.open_dataset(infile)
    data = data.sel(lon=slice(lonmin, lonmax), lat=slice(latmin, latmax))
    data = data.mean(dim=['lon', 'lat'])
    if os.path.isfile(outfile):
        os.remove(outfile)
    data.to_netcdf(outfile, format='NETCDF4')

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    make_subset(
        infile=os.path.abspath(args.infile),
        outfile=os.path.abspath(args.outfile),
        lonmin=args.X0,
        lonmax=args.X1,
        latmin=args.Y0,
        latmax=args.Y1
    )

if __name__ == "__main__":
    main()
