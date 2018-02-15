#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot the Chiclet diagram
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of plot")
parser.add_argument("--s2s", help="the filename of the s2s data")
parser.add_argument("--rain", help="the filename of the rainfall data")

def main():
    """Run through the code
    """
    args = parser.parse_args()
    
    modeled = xr.open_dataarray(args.s2s)
    modeled['S'] = pd.to_datetime(modeled['S'].values).date
    modeled['S'] = pd.to_datetime(modeled['S'].values)
    modeled['L'] = np.int_(modeled['L'].astype('timedelta64[D]') / np.timedelta64(1, 'D'))
    modeled = modeled.to_dataframe().dropna()
    modeled = modeled.reset_index()
    modeled['target_date'] = modeled['S'] + modeled['L'].apply(np.ceil).apply(lambda x: pd.Timedelta(x, unit='D'))
    modeled = modeled.loc[np.logical_and(modeled['target_date'] >= '2015-11-01', modeled['target_date'] <= '2016-02-29')]
    modeled = modeled.set_index(['target_date', 'L', 'M'])

    lpr = Region(lon = [-59.75, -55.75], lat = [-27.75, -22.75])
    obs = xr.open_dataset(args.rain)['raw'].sel(
        lon = slice(lpr.lonmin, lpr.lonmax),
        lat = slice(lpr.latmin, lpr.latmax)).mean(dim=['lon', 'lat']).to_pandas()
    climatology = obs.mean()
    obs = obs['2015-11-01':'2016-02-29']

    modeled['tpa'] = modeled['tp'] - climatology
    forecast = modeled.to_xarray()['tpa'].mean(dim='M')

    print(forecast.min())

    fig,axes = plt.subplots(ncols=1, nrows=2, figsize=((13, 6)), gridspec_kw = {'height_ratios':[2.7, 1]}, sharex=True)
    ax=axes[0] # Chiclet
    C1 = forecast.plot.pcolormesh(
        x='target_date', y='L', cmap = 'BrBG', ax=ax, 
        add_colorbar=False, add_labels=False,
        vmin=-15, vmax=15,
        )
    ax.set_ylabel("Lead Time (Days)")
    ax.set_xticks([])
    ax.grid(True)

    ax = axes[1] # Observed Rainfall
    ax.fill_between(obs.index, obs)
    ax.axhline(climatology, label='climatology', c='black', linewidth=0.95)
    ax.grid(True)
    ax.invert_yaxis()
    ax.set_ylabel("Rainfall [mm/day]")
    ax.set_xlabel("Date")
    ax.legend()

    fig.tight_layout()
    fig.subplots_adjust(right=0.94)
    cax = fig.add_axes([0.97, 0.4, 0.01, 0.55])
    cbar = fig.colorbar(C1, cax = cax)
    cbar.set_label("Ensemble-Mean Rainfall Forecast [mm/day]", rotation=270)
    cbar.ax.get_yaxis().labelpad = 20

    fig.savefig(args.outfile, bbox_inches="tight")

if __name__ == "__main__":
    main()
