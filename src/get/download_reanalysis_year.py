#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download a single year of 6-Hour Reanalysis V2 data from
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""

import argparse
import os
import xarray as xr
import numpy as np

parser = argparse.ArgumentParser()  # pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--year", help="the year of data to download")
parser.add_argument("--coord_system", help="the coordinate system containing the data")
parser.add_argument("--var", help="the name of the variable")
parser.add_argument("--level", help="the pressure level")


def download_data(coord_system, var, year, level, outfile):
    """Download a single year of reanalysis V2 data
    """
    # Open a connection with the DODs URL
    base_url = "https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2"
    full_url = "{}/{}/{}.{}.nc".format(base_url, coord_system, var, year)
    data = xr.open_dataset(full_url, decode_cf=False).sel(level=level)

    # Need to have the variable name since we created a data set not array
    varname = list(data.data_vars.keys())[0]

    # Have to mess around a bit with the cf conventions for this data set
    data[varname].attrs.pop("missing_value")
    data = xr.decode_cf(data, mask_and_scale=True, decode_times=True)[varname]

    # Save to file
    if os.path.isfile(outfile):
        os.remove(outfile)
    data.to_netcdf(outfile, format="NETCDF4", mode="w")


def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    year = int(args.year)
    coord_system = args.coord_system
    var = args.var
    level = int(args.level)
    download_data(
        year=year, outfile=outfile, coord_system=coord_system, var=var, level=level
    )


if __name__ == "__main__":
    main()
