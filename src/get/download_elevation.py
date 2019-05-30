#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download elevation data
http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/X/-180/0.025/180/GRID/Y/-90/0.025/90/GRID/dods
"""

import argparse
import os
import xarray as xr
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()  # pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")


def download_data(outfile):
    """Download the elevation data
    """
    # read in the data
    url = "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/"
    url += "X/-180/0.025/180/GRID/Y/-90/0.025/90/GRID/dods"
    data = xr.open_dataarray(url)  # doesn't follow time conventions

    # save to file
    if os.path.isfile(outfile):
        os.remove(outfile)
    data.to_netcdf(outfile, format="NETCDF4", mode="w")


def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    download_data(outfile=outfile)


if __name__ == "__main__":
    main()
