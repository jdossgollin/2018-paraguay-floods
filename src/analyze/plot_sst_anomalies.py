#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot SST Anomalies
"""

import argparse
import os

import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import cartopy.crs as ccrs
import cartopy.feature
import colorcet as cc

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the figure to save")
parser.add_argument("--sst", help="the filename of the SST data")
parser.add_argument("--wt", help="the filename of the weather type data")

def main():
    """Run everything
    """
    args = parser.parse_args()

    # Read in and parse the raw data
    sea_temp = xr.open_dataarray(args.sst)
    wt = xr.open_dataarray(args.wt).to_dataframe(name='wtype')
    wt['T'] = wt.index.to_period("M")
    wt = wt.groupby(['T', 'wtype']).size().unstack(fill_value=0)
    wt = wt.sort_values(4, ascending=False).head()

    # Plot options
    n_months = 15
    map_proj = ccrs.PlateCarree(central_longitude=-60)
    data_proj = ccrs.PlateCarree()
    figsize = (10, 8)
    dipole = Region(lon=[-30,-10], lat=[-10,-40])
    cmap = cc.cm['coolwarm']

    # Times to plot
    times = wt.sort_values(4, ascending=False).head(n_months).index.to_timestamp()
    composite_wt4 = sea_temp.sel(T = np.in1d(sea_temp['T'], times)).mean(dim='T')

    # Set up 2 plots
    fig, axes = plt.subplots(
        nrows=2, ncols=1, subplot_kw={'projection': map_proj},
        figsize=figsize, sharex=True, sharey=True
    )

    # First: Months with most WT4
    ax = axes[0]
    C1 = composite_wt4.plot.contourf(
        ax=ax, transform=data_proj,
        cmap=cmap,
        levels=np.linspace(-0.6, 0.6, 13),
        extend='both',
        add_colorbar=True,
        add_labels=False
    )
    ax.add_patch(dipole.as_patch(color='black'))


    # Second: Plot December 2015
    ax = axes[1]
    C2 = sea_temp.sel(T = '2015-12-01').plot.contourf(
        ax=ax, transform=data_proj,
        cmap=cmap,
        levels=np.linspace(-2.5, 2.5, 11),
        extend='both',
        add_colorbar=True,
        add_labels=False
    )
    ax.add_patch(dipole.as_patch(color='black'))
    ax.set_xlim([-120, 120])
    ax.set_ylim([-70, 15])

    # Format axes
    viz.format_axes(
        axes, extent = None, border=True,
        xticks=np.linspace(-180, 180, 19), yticks=np.linspace(-90, 90, 10)
    )
    for ax in axes.flat:
        ax.set_xlim([-50, 80]) # is relative to central longitude
        ax.set_ylim([-50, 10])

    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
