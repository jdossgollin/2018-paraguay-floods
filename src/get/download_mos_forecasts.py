#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download MOS forecasts from IRI Data Library
"""

import argparse
import xarray as xr

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--model", help="name of the model")
parser.add_argument("--outfile", help="the filename of the data to save")

def get_forecast(model, type):
    """
    """
    base_url = 'http://iridl.ldeo.columbia.edu/ds%3A/home/.agmunoz/.Paraguay/'
    url = base_url + '{}/'.format(model)
    if type == 'forecast':
        url += '.Odds_1-7Dec2015/dods'
    elif type == 'skill':
        url += '.2AFCProbFcsts/dods'
    elif type == 'ignorance':
        url += '.IGNProbFcsts/dods'
    else:
        raise ValueError('type is not valid')
    ds = xr.open_dataarray(url)
    ds = ds.sortby(['X', 'Y']) # be more consistent
    if ds.ndim > 2:
        ds = ds.isel(time=0).drop('time')
    ds.coords['model'] = model
    return(ds)


def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    if os.path.isfile(outfile):
        os.remove(outfile)
    data.to_netcdf(outfile, format='NETCDF4', mode='w')
    download_data(outfile=outfile)

if __name__ == "__main__":
    main()
