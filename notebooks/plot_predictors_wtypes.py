#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot predictors and weather types
"""

import argparse
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--mjo", help="The MJO data")
parser.add_argument("--nino", help="The NINO data")
parser.add_argument("--wt", help="The weather types")
parser.add_argument("--dipole", help="The dipole time series")
parser.add_argument("--n_eof", type=int)

def main():
    # Read in raw data
    args = parser.parse_args()
    
    mjo = xr.open_dataset(args.mjo).to_dataframe()
    mjo.loc[mjo['amplitude'] < 1, 'phase'] = 0
    mjo = pd.get_dummies(mjo['phase'])
    mjo.columns = ['MJO' + str(c) for c in mjo.columns]
    
    nino = xr.open_dataarray(args.nino).to_dataframe(name='NINO 3.4')
    nino_daily = nino.resample('1D').ffill()
    
    wt = xr.open_dataarray(args.wt).to_dataframe(name='WT')
    wt = pd.get_dummies(wt['WT'],  prefix='WT')

    dipole = xr.open_dataarray(args.dipole).to_dataframe(name='SCAD').resample('1D').ffill()

    # Join everything together
    daily = mjo.join(nino_daily).join(dipole).join(wt).dropna()
    monthly = daily.resample('1M').mean().dropna()

    # Get the predictor, EOF, and WT columns
    predictors = mjo.columns.tolist()
    predictors.append('SCAD')
    predictors.append('NINO 3.4')
    wts = wt.columns.tolist()

    # Get the monthly WT and EOF correlations
    correlations = monthly.corr(method='spearman')
    wt_correlations = correlations.loc[predictors, wts]

    # convert to xarray
    wt_correlations = xr.DataArray(
        wt_correlations, 
        coords={'Predictor': predictors, 'Weather Type': np.arange(1, 7)},
        dims=['Predictor', 'Weather Type']).to_pandas()

    # Plot
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(9, 6), sharex=False, sharey=True)
    keywords = dict(cmap='PuOr', annot=True, vmin=-0.4, vmax=0.4)
    sns.heatmap(wt_correlations,ax=axes, **keywords)

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
