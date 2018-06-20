#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot WT Occurrence on ENSO and MJO
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import string

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--wt", help="The weather type data")
parser.add_argument("--nino", help="The streamfunction data file")
parser.add_argument("--mjo", help="The streamfunction data file")

def main():
    args = parser.parse_args()

    wt = xr.open_dataarray(args.wt).to_dataframe(name='wtype')
    mjo = xr.open_dataset(args.mjo).to_dataframe()
    enso = xr.open_dataarray(args.nino).to_dataframe(name='nino_34').resample('1D').ffill()
    mrg = wt.join(mjo).join(enso)
    
    mrg.loc[mrg['amplitude'] < 1, 'phase'] =  0
    mrg['enso_state'] = 0
    mrg.loc[mrg['nino_34'] < -1, 'enso_state'] = -1
    mrg.loc[mrg['nino_34'] > 1, 'enso_state'] = 1
    
    conditional = mrg.groupby(['phase', 'enso_state'])['wtype'].apply(lambda g: g.value_counts() / g.size)
    conditional = conditional.to_xarray()
    anomaly = conditional - conditional.mean(dim=['level_2'])

    # Bootstrap simulations
    n_sim = 5000
    anomalies = []
    for i in np.arange(n_sim):
        wt_seq = np.random.choice(mrg['wtype'], size=mrg.shape[0], replace=True)
        simulated = pd.DataFrame({'wtype': wt_seq, 'phase': mrg['phase'], 'enso_state': mrg['enso_state']})
        conditional = simulated.groupby(['phase', 'enso_state'])['wtype'].apply(lambda g: g.value_counts() / g.size)
        conditional = conditional.to_xarray()
        anomalies.append(conditional - conditional.mean(dim=['level_2']))
    anomalies = xr.concat(anomalies, dim='temp')

    # Select significant simulations
    alpha = 0.10
    upper = anomalies.quantile(1-alpha/2, dim='temp')
    lower = anomalies.quantile(alpha/2, dim='temp')
    significant = np.logical_or((anomaly >= upper), (anomaly <= lower))


    # Plot
    enso_states = {-1: 'La Niña', 0: 'Neutral', 1: 'El Niño'}
    p = anomaly.where(significant).plot(
        x='level_2', y='phase', col='enso_state',
        cmap='PuOr',
        figsize=(12, 5)
    )
    for i,es in enumerate(enso_states):
        ax = p.axes.flat[i]
        ax.set_title(enso_states.get(i-1, ''))
        ax.set_xlabel('Weather Type')
    p.axes[0,0].set_ylabel('MJO Phase')
    p.cbar.set_label('Anomalous Probability of Occurrence', rotation=270)
    p.cbar.ax.get_yaxis().labelpad = 20
    plt.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
