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

parser = argparse.ArgumentParser()  # pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")


def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()

    url = "http://iridl.ldeo.columbia.edu/expert/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/"
    url += ".Reyn_SmithOIv2/.monthly/.ssta/dods"  # split lines
    data = xr.open_dataarray(url, decode_times=False)  # doesn't follow time conventions

    # parse the time manually
    time = np.int_(np.floor(data["T"]))
    year = 1960 + time // 12
    month = 1 + time % 12
    time = pd.to_datetime(year * 10000 + month * 100 + 1, format="%Y%m%d")
    data["T"] = time

    data = data.rename({"X": "lon", "Y": "lat", "T": "time"})
    longitudes = data["lon"].values
    longitudes[np.where(longitudes > 180)] -= 360
    data["lon"].values = longitudes

    # sort
    data = data.sortby("lon").sortby("lat").sortby("time")

    # save to file
    if os.path.isfile(args.outfile):
        os.remove(args.outfile)
    data.to_netcdf(args.outfile, format="NETCDF4", mode="w")


if __name__ == "__main__":
    main()
