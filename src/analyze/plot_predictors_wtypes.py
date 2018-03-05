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
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--mjo", help="The MJO data")
parser.add_argument("--nino", help="The NINO data")
parser.add_argument("--wt", help="The Weather Type sequence")

def main():
    # Read in raw data
    args = parser.parse_args()
    
    mjo = xr.open_dataset(args.mjo).to_dataframe()[['phase']]
    mjo = pd.get_dummies(mjo['phase'])
    mjo.columns = ['MJO' + str(c) for c in mjo.columns]
    nino = xr.open_dataarray(args.nino).to_dataframe(name='NINO 3.4')
    nino_daily = nino.resample('1D').ffill()
    wt = xr.open_dataarray(args.wt).to_dataframe(name='Weather Type')
    wt = pd.get_dummies(wt['Weather Type'])
    wt.columns = ['WT ' + str(w) for w in wt.columns]

    # Join everything together
    daily = mjo.join(nino_daily).join(wt).dropna()
    monthly = daily.resample('1M').mean().dropna()

    # Get the daily and monthly correlations
    predictors = mjo.columns.tolist()
    predictors.append('NINO 3.4')
    wtypes = wt.columns.tolist()
    daily_correlations = np.zeros((len(predictors), len(wtypes)))
    monthly_correlations = np.zeros((len(predictors), len(wtypes)))
    for i, pred in enumerate(predictors):
        for j, w in enumerate(wtypes):
            daily_correlations[i, j] = daily.corr().loc[pred, w]
            monthly_correlations[i, j] = monthly.corr().loc[pred, w]

    # convert to xarray
    daily_correlations = xr.DataArray(
        daily_correlations, 
        coords={'Predictor': predictors, 'Weather Type': np.arange(1, 7)},
        dims=['Predictor', 'Weather Type']).to_pandas()
    monthly_correlations = xr.DataArray(
        monthly_correlations, 
        coords={'Predictor': predictors, 'Weather Type': np.arange(1, 7)},
        dims=['Predictor', 'Weather Type']).to_pandas()

    # Plot
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), sharex=True, sharey=True)
    sns.heatmap(daily_correlations, cmap='PuOr', annot=True, ax=axes[0], vmin=-0.15, vmax=0.15)
    axes[0].set_title('Daily Correlation')
    sns.heatmap(monthly_correlations, cmap='PuOr', annot=True, ax=axes[1], vmin=-0.4, vmax=0.4)
    axes[1].set_title('Monthly Correlation')

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
