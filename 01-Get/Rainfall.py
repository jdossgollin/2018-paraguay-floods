'''
Here we download Get the CPC data from the IRI Data Library.
We only get rainfall estimate -- neglects information on number of stations used in analysis.
Please see caveats and documentation on IRI Server at http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/
'''

import pandas as pd
import numpy as np
import xarray as xr
import datetime
import os
from paraguayfloodspy.pars  import GetPars

# Work with Times from the IRIDL
def convert_t_to_time(Tvec):
    times = np.array([datetime.date(1960, 1, 1) + datetime.timedelta(np.int(ti)) for ti in Tvec])
    return(np.array(times))
def convert_time_to_t(date):
    date_diff = date - datetime.date(1960,1,1)
    T = date_diff.days
    return(T)

def IRICPCYear(year, verbose=True):
        if verbose:
            print('Downloading data for {}...'.format(year))
        # realtime or retro?
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
        return(ds)

def GetFileName(year):
    fn = "_data/rainfall/raw/cpc_{}.nc".format(year)
    return(fn)

def main():
    pars = GetPars('time')
    syear, eyear = pars['syear'], pars['eyear']
    overwrite = False

    # Loop through
    for year_i in np.arange(syear, eyear+1):
        fn = GetFileName(year=year_i)
        if os.path.isfile(fn) and not overwrite:
            print("\tData for {} already exists -- not re-downloading".format(year_i))
        else:
            ds = IRICPCYear(year=year_i, verbose=True)
            ds.to_netcdf(fn, format='NETCDF4')

if __name__ == '__main__':
    main()
