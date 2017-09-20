'''
Download one year of CPC Rainfall Data from the IRI Data Library.
We only get rainfall estimate -- neglects information on number of stations used in analysis.
Please see caveats and documentation on IRI Server at http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/
'''

import pandas as pd
import numpy as np
import xarray as xr
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--year', nargs=1, type=int, help='The year of data to download')
parser.add_argument('--outfile', nargs=1, help='The output file to save')

# Work with Times from the IRI DL
def convert_t_to_time(Tvec):
    times = np.array([datetime.date(1960, 1, 1) + datetime.timedelta(np.int(ti)) for ti in Tvec])
    return(np.array(times))
def convert_time_to_t(date):
    date_diff = date - datetime.date(1960,1,1)
    T = date_diff.days
    return(T)

def main():
    # parse the arguments
    args = parser.parse_args()
    year = args.year[0]
    outfile = args.outfile[0]

    # Get the URL
    if year >= 1979 and year <= 2005:
        url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.RETRO/.rain/dods'
    elif year >= 2006 and year <= 2016:
        url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.REALTIME/.rain/dods'
    else:
        raise ValueError('You have entered an invalid year. {} is outside range [1979, 2016]'.format(year))

    # get the data
    Tstart = convert_time_to_t(datetime.date(year, 1, 1))
    Tend = convert_time_to_t(datetime.date(year, 12, 31))
    ds = xr.open_dataarray(url, decode_times=False)
    ds = ds.sel(T = slice(Tstart, Tend))
    ds.load() # force it to download

    # convert to more standard format
    ds = ds.rename({'X': 'lon', 'Y': 'lat', 'T': 'time'})
    ds['time'] = convert_t_to_time(ds['time'])
    ds['time'] = ds['time'].astype('datetime64')

    # Save to file
    ds.to_netcdf(outfile, format='NETCDF4')

if __name__ == '__main__':
    main()
