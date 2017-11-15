'''
Get model forecasts, skill, and ignorance from Angel's Data Library page
'''

import numpy as np
import xarray as xr
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--forecasts', nargs=1, help='The output file to save!')
parser.add_argument('--skill', nargs=1, help='The output file to save!')
parser.add_argument('--ignorance', nargs=1, help='The output file to save!')

def get_forecast(model, type):
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
    if ds.ndim > 2:
        ds = ds.isel(time=0).drop('time')

    ds.coords['model'] = model

    return(ds)

def main():

    # parse the arguments
    args = parser.parse_args()

    model_names = pd.Series(['Raw', 'XLR', 'HXLR', 'PCR', 'CCA'])

    forecasts = xr.concat([get_forecast(m, type='forecast') for m in model_names], dim='model')
    forecasts.to_netcdf(args.forecasts[0], format='NETCDF4')

    skill = xr.concat([get_forecast(m, type='skill') for m in model_names], dim='model')
    skill.to_netcdf(args.skill[0], format='NETCDF4')

    ignorance = xr.concat([get_forecast(m, type='ignorance') for m in model_names], dim='model')
    ignorance.to_netcdf(args.ignorance[0], format='NETCDF4')

if __name__ == '__main__':
    main()
