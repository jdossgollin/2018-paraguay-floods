'''
Subsetting, Anomalies, and Climatologies
'''

import xarray as xr
import glob
import numpy as np
from paraguayfloodspy.xrutil import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mode', nargs=1, help='Either [rain] or [reanalysis]')
parser.add_argument('--pattern', nargs=1, help='The pattern of files to read in')
parser.add_argument('--latlim', type=float, nargs=2, help = 'LATMIN, LATMAX')
parser.add_argument('--lonlim', type=float, nargs=2, help = 'LONMIN, LATMAX')
parser.add_argument('--years', type=int, nargs=2, help = 'LONMIN, LATMAX')
parser.add_argument('--outfile', nargs=1, help='The output file to save')

def main():
    args = parser.parse_args()
    latmin, latmax = np.min(args.latlim), np.max(args.latlim)
    lonmin, lonmax = np.min(args.lonlim), np.max(args.lonlim)
    syear, eyear = np.min(args.years), np.max(args.years)

    def transfer_fn(ds, mode, lonmin, lonmax, latmin, latmax):
        '''
        This function sub-sets data as we read it
        '''
        assert lonmax > lonmin, "lonmax must be greater than lonmin"
        assert latmax > latmin, "latnmax must be greater than latmin"
        if mode == 'rain':
            ds = ds.sel(lon = slice(lonmin, lonmax), lat = slice(latmin, latmax))
        elif mode == 'reanalysis':
            ds = ds.sel(lon = slice(lonmin, lonmax), lat = slice(latmax, latmin))
        else:
            raise ValueError('mode must be rain or reanalysis')
        return(ds)

    # Read in raw data
    fnames = glob.glob(args.pattern[0])
    if len(fnames) < 1:
        raise ValueError("Pattern {} doesn't match any files".format(args.pattern[0]))

    # subset data when we read it in
    trans_lam = lambda ds: transfer_fn(ds, mode=args.mode[0], lonmin=lonmin, lonmax=lonmax, latmin=latmin, latmax=latmax)
    raw = read_netcdfs(fnames, dim='time', transform_func=trans_lam)
    if args.mode[0] =='rain':
        raw = raw['rain']
    elif args.mode[0] == 'reanalysis':
        # reanalysis data: shift 12 hours (end-of-day time) and sample to daily
        time_old = raw.time.values
        time_new = time_old + np.timedelta64(12, 'h')
        raw['time'] = time_new
        raw = raw.resample('1D', dim = 'time')
        raw = raw['streamfunction']
    else:
        raise ValueError('mode must be rain or reanalysis')

    # calculate anomaly
    anomaly = SmoothAnomaly(raw, year0=1980, year1=2010, window=30, time_name='time')
    anomaly = anomaly.reset_coords().drop('doy')
    if args.mode[0] =='rain':
        anomaly = anomaly['rain']
    elif args.mode[0] == 'reanalysis':
        anomaly = anomaly['streamfunction']
    else:
        raise ValueError('mode must be rain or reanalysis')

    # combine and subset and save
    combined = xr.Dataset({'raw': raw, 'anomaly': anomaly})
    combined = combined.sel(time = slice('{}-11-01'.format(syear), '{}-02-28'.format(eyear)))
    combined = combined.sel(time = np.in1d(combined['time.month'], [11, 12, 1, 2]))
    combined.to_netcdf(args.outfile[0], format='NETCDF4')

if __name__ == '__main__':
    main()
