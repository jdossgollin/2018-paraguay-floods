#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Area-averaged gradient
"""

import argparse
import os
import xarray as xr
import numpy as np

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--infile", help="the input data")
parser.add_argument("--X0", type=float, help="lon min")
parser.add_argument("--X1", type=float, help="lon max")
parser.add_argument("--Y0", type=float, help="lat min")
parser.add_argument("--Y1", type=float, help="lat max")

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    ds = xr.open_dataarray(args.infile)
    ds = ds.sel(lon=slice(args.X0, args.X1), lat=slice(args.Y0, args.Y1))
    ddy = np.gradient(ds.values)[1]
    ddy = xr.DataArray(ddy, coords=ds.coords, dims=ds.dims)
    ddy = ddy.mean(dim=['lon', 'lat'])
    ddy.to_netcdf(args.outfile, format='NETCDF4', mode='w')

if __name__ == "__main__":
    main()
