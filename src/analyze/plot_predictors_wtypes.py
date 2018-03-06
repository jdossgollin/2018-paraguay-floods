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
from sklearn.decomposition import PCA

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--mjo", help="The MJO data")
parser.add_argument("--nino", help="The NINO data")
parser.add_argument("--psi_wtype", help="The streamfunction over the weather typing region")
parser.add_argument("--sst", help="The SST anomaly data")
parser.add_argument("--n_eof", type=int)

def main():
    # Read in raw data
    args = parser.parse_args()
    
    mjo = xr.open_dataset(args.mjo).to_dataframe()[['phase']]
    mjo = pd.get_dummies(mjo['phase'])
    mjo.columns = ['MJO' + str(c) for c in mjo.columns]
    
    nino = xr.open_dataarray(args.nino).to_dataframe(name='NINO 3.4')
    nino_daily = nino.resample('1D').ffill()
    
    psi = xr.open_dataset(args.psi_wtype)['anomaly']
    psi_stacked = psi.stack(grid=['lon', 'lat'])
    pca = PCA(n_components=args.n_eof).fit(psi_stacked)
    pc_ts = pca.transform(psi_stacked)
    pc_ts = pd.DataFrame(pc_ts, index=psi_stacked['time'])
    pc_ts.columns = ['EOF{}'.format(i) for i in np.arange(1, args.n_eof + 1)]

    sst = xr.open_dataarray(args.sst).rename({'X': 'lon', 'Y': 'lat', 'T': 'time'})
    sst = sst.sel(lon=slice(360-30, 360-10), lat=slice(-40, -15)).mean(dim=['lon', 'lat'])
    sst = sst.to_dataframe(name='Dipole').resample('1D').ffill()

    # Join everything together
    daily = mjo.join(nino_daily).join(pc_ts).join(sst).dropna()
    monthly = daily.resample('1M').mean().dropna()

    # Get the daily and monthly correlations
    predictors = mjo.columns.tolist()
    predictors.append('NINO 3.4')
    predictors.append('Dipole')
    eofs = pc_ts.columns.tolist()
    daily_correlations = np.zeros((len(predictors), len(eofs)))
    monthly_correlations = np.zeros((len(predictors), len(eofs)))
    for i, pred in enumerate(predictors):
        for j, pc in enumerate(eofs):
            daily_correlations[i, j] = daily.corr().loc[pred, pc]
            monthly_correlations[i, j] = monthly.corr().loc[pred, pc]

    # convert to xarray
    daily_correlations = xr.DataArray(
        daily_correlations, 
        coords={'Predictor': predictors, 'Streamfunction EOF': np.arange(1, args.n_eof + 1)},
        dims=['Predictor', 'Streamfunction EOF']).to_pandas()
    monthly_correlations = xr.DataArray(
        monthly_correlations, 
        coords={'Predictor': predictors, 'Streamfunction EOF': np.arange(1, args.n_eof + 1)},
        dims=['Predictor', 'Streamfunction EOF']).to_pandas()

    # Plot
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharex=True, sharey=True)
    sns.heatmap(daily_correlations, cmap='PuOr', annot=True, ax=axes[0], vmin=-0.15, vmax=0.15)
    axes[0].set_title('Daily Correlation')
    sns.heatmap(monthly_correlations, cmap='PuOr', annot=True, ax=axes[1], vmin=-0.4, vmax=0.4)
    axes[1].set_title('Monthly Correlation')

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
