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
parser.add_argument("--dipole", help="The dipole time series")
parser.add_argument("--n_eof", type=int)

def main():
    # Read in raw data
    args = parser.parse_args()
    
    mjo = xr.open_dataset(args.mjo).to_dataframe()
    mjo.to_csv('~/Downloads/mjo.csv')
    mjo.loc[mjo['amplitude'] < 1, 'phase'] = 0
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

    dipole = xr.open_dataarray(args.dipole).to_dataframe(name='Dipole').resample('1D').ffill()

    # Join everything together
    daily = mjo.join(nino_daily).join(dipole).join(pc_ts).dropna()
    monthly = daily.resample('1M').mean().dropna()

    # Get the predictor, EOF, and WT columns
    predictors = mjo.columns.tolist()
    predictors.append('Dipole')
    predictors.append('NINO 3.4')
    eofs = pc_ts.columns.tolist()

    # Get the monthly WT and EOF correlations
    correlations = monthly.corr(method='spearman')
    eof_correlations = correlations.loc[predictors, eofs]

    # convert to xarray
    eof_correlations = xr.DataArray(
        eof_correlations, 
        coords={'Predictor': predictors, 'Streamfunction EOF': np.arange(1, args.n_eof + 1)},
        dims=['Predictor', 'Streamfunction EOF']).to_pandas()

    # Plot
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(9, 6), sharex=False, sharey=True)
    keywords = dict(cmap='PuOr', annot=True, vmin=-0.4, vmax=0.4, linewidth=1)
    sns.heatmap(eof_correlations,ax=axes, **keywords)

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
