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
parser.add_argument("--psi_wtype", help="The streamfunction over the weather typing region")
parser.add_argument("--n_eof", type=int)
parser.add_argument("--wtype", help='path to the weather type data')

def main():
    # Read in raw data
    args = parser.parse_args()
    
    psi = xr.open_dataset(args.psi_wtype)['anomaly']
    psi_stacked = psi.stack(grid=['lon', 'lat'])
    pca = PCA(n_components=args.n_eof).fit(psi_stacked)
    pc_ts = pca.transform(psi_stacked)
    pc_ts = pd.DataFrame(pc_ts, index=psi_stacked['time'])
    pc_ts.columns = ['EOF{}'.format(i) for i in np.arange(1, args.n_eof + 1)]

    wt = xr.open_dataarray(args.wtype).to_dataframe(name='wtype')
    wt = pd.get_dummies(wt['wtype'])
    wt.columns = ['WT' + str(c) for c in wt.columns]

    # Join everything together
    daily = pc_ts.join(wt).dropna()
    monthly = daily.resample('1M').mean()

    # Get the monthly WT and EOF correlations
    correlations = monthly.corr(method='spearman')
    correlations = correlations.loc[pc_ts.columns.tolist(), wt.columns.tolist()]

    # Plot
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 5), sharex=False, sharey=True)
    keywords = dict(cmap='PuOr', annot=True, vmin=-0.75, vmax=0.75)
    sns.heatmap(correlations, ax=axes, **keywords)

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
