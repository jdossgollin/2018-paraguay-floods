'''
Get Area-Averaged S2S Forecast Rainfall
'''

import xarray as xr
import numpy as np
import pandas as pd
import datetime
import os
from paraguayfloodspy.pars import GetPars

def GetURL(x0, x1, y0, y1):
    url = 'http://iridl.ldeo.columbia.edu/home/.mbell/.ECMWF/.S2Stest/.S2S/.ECMF_ph2/.forecast/.perturbed/.sfc_precip/.tp/'
    url += 'X/{}/{}/RANGEEDGES/'.format(x0, x1)
    url += 'Y/{}/{}/RANGEEDGES/'.format(y0, y1)
    url += '[X+Y]average/'
    url += 'L+differences/'
    url += 'dods'
    return(url)

def main():
    print("\nWelcome to S2S.py")
    pars = GetPars('all')
    overwrite = False

    url = GetURL(
        x0=pars['rpy_rain']['lonmin'],
        x1=pars['rpy_rain']['lonmax'],
        y0=pars['rpy_rain']['latmin'],
        y1=pars['rpy_rain']['latmax']
    )
    fname = "_data/s2s/AreaAvg.nc"

    if (os.path.isfile(fname) and not overwrite):
        print("S2S data already exists -- will not re-download")
    else:
        print('Downloading S2S data from {}'.format(url))
        ds = xr.open_dataarray(url)
        ds = ds.sel(S = slice('2015-09-01', '2016-02-29'))
        ds['L'] = ds['L']
        ds.to_netcdf(fname)

if __name__ == '__main__':
    main()
