'''
Get Area-Averaged S2S Forecast Rainfall
'''

import xarray as xr
import numpy as np
import pandas as pd
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--latlim', type=float, nargs=2, help = 'LATMIN, LATMAX')
parser.add_argument('--lonlim', type=float, nargs=2, help = 'LONMIN, LATMAX')
parser.add_argument('--outfile', nargs=1, help='The output file to save')

def GetURL(x0, x1, y0, y1):
    url = 'http://iridl.ldeo.columbia.edu/home/.mbell/.ECMWF/.S2Stest/.S2S/.ECMF_ph2/.forecast/.perturbed/.sfc_precip/.tp/'
    url += 'X/{}/{}/RANGEEDGES/'.format(x0, x1)
    url += 'Y/{}/{}/RANGEEDGES/'.format(y0, y1)
    url += '[X+Y]average/'
    url += 'L+differences/'
    url += 'dods'
    return(url)

def main():

    args = parser.parse_args()
    latmin, latmax = np.min(args.latlim), np.max(args.latlim)
    lonmin, lonmax = np.min(args.lonlim), np.max(args.lonlim)

    url = GetURL(x0=lonmin, x1=lonmax, y0=latmin, y1=latmax)
    outfile = args.outfile[0]

    print('Downloading S2S data from {}'.format(url))
    ds = xr.open_dataarray(url)
    ds = ds.sel(S = slice('2015-09-01', '2016-02-29'))
    ds['L'] = ds['L']
    ds.to_netcdf(outfile, format="NETCDF4")

if __name__ == '__main__':
    main()
