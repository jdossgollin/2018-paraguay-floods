#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script reads in, parses, downloads, and saves to file the data for
a single year from the CPC Global Unified Precipitation Data Set from
http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/
"""

import argparse
import datetime
import os
import xarray as xr
import numpy as np

parser = argparse.ArgumentParser()  # pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--year", help="the year of data to download")


def convert_t_to_time(time_vec):
    """Parse the times from the IRI Data Library
    """
    time = np.array(
        [datetime.date(1960, 1, 1) + datetime.timedelta(np.int(ti)) for ti in time_vec]
    )
    return np.array(time)


def convert_time_to_t(date):
    """Turn a date into the appropriate IRI Data Library Format
    """
    date_diff = date - datetime.date(1960, 1, 1)
    time_dl = date_diff.days
    return time_dl


def download_data(year, outfile):
    """Download data for a single year
    """
    base_url = "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/"
    base_url += ".UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0"
    if year >= 1979 and year <= 2005:
        url = base_url + "/.RETRO/.rain/dods"
    elif year >= 2006 and year <= 2019:
        url = base_url + "/.REALTIME/.rain/dods"
    else:
        raise ValueError("You have entered an invalid year {}".format(year))

    # get the start and end times as IRIDL strings
    dt_start = convert_time_to_t(datetime.date(year, 1, 1))
    dt_end = convert_time_to_t(datetime.date(year, 12, 31))

    # Read in the raw data, rename the variables
    rain_year = xr.open_dataarray(url, decode_times=False)
    rain_year = rain_year.sel(T=slice(dt_start, dt_end)).load()
    rain_year = rain_year.rename({"X": "lon", "Y": "lat", "T": "time"})

    # convert the time data
    rain_year["time"] = convert_t_to_time(rain_year["time"])
    rain_year["time"] = rain_year["time"].astype("datetime64")

    # standardize longitudes and latitudes
    lon_new = rain_year["lon"].values.copy()
    lon_new[np.where(lon_new > 180.0)] -= 360
    rain_year["lon"].values = lon_new
    rain_year = rain_year.sortby("lon")
    rain_year = rain_year.sortby("lat")
    rain_year.attrs["year"] = year

    # save the data to file
    if os.path.isfile(outfile):
        os.remove(outfile)
    rain_year.to_netcdf(outfile, format="NETCDF4", mode="w")


def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    year = int(args.year)
    download_data(year, outfile)


if __name__ == "__main__":
    main()
