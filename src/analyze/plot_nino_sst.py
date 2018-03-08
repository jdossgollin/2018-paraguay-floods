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
import string

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the figure to save")
parser.add_argument("--sst", help="the filename of the SST data")

def main():
    """Run everything
    """
    args = parser.parse_args()

    sea_temp = xr.open_dataarray(args.sst)
    sea_temp = sea_temp.sel(time = np.in1d(sea_temp['time.month'], [11, 12, 1, 2]))
    rain = xr.open_dataset('data/processed/rain.nc')['anomaly']

    # Plot options
    map_proj = ccrs.PlateCarree(central_longitude=-60)
    data_proj = ccrs.PlateCarree()
    figsize = (18, 9)
    dipole = Region(lon=[-30,-10], lat=[-10,-40])

    
    nino_years = [1982, 1997, 2015]

    # Set up plots
    fig, axes = plt.subplots(
        nrows=4, ncols=len(nino_years), subplot_kw={'projection': map_proj},
        figsize=figsize, sharex=True, sharey=True
    )

    for i, yr in enumerate(nino_years):
        sst_keywords = dict(
            transform=data_proj,
            cmap=cc.cm['coolwarm'],
            levels=np.linspace(-3, 3, 13),
            add_colorbar=True,
            add_labels=False,
            extend='both',
        )

        rain_keywords = dict(
            transform=data_proj,
            cmap='BrBG',
            levels=np.linspace(-7, 7, 15),
            add_colorbar=False,
            add_labels=False,
            extend='both',
        )
        
        # NOVEMBER
        ax = axes[0, i]
        selector = lambda ds: ds.sel(time = slice('{}-11-01'.format(yr), '{}-11-30'.format(yr))).mean(dim='time')
        rain_sub = selector(rain)
        sst_sub = selector(sea_temp)
        sst_sub.plot.contourf(ax=ax, **sst_keywords)
        rain_sub.plot.contourf(ax=ax, **rain_keywords)
        ax.add_patch(dipole.as_patch(color='blue'))
        ax.set_title('November {}'.format(yr))

        # DECEMBER
        ax = axes[1, i]
        selector = lambda ds: ds.sel(time = slice('{}-12-01'.format(yr), '{}-12-31'.format(yr))).mean(dim='time')
        rain_sub = selector(rain)
        sst_sub = selector(sea_temp)
        sst_sub.plot.contourf(ax=ax, **sst_keywords)
        rain_sub.plot.contourf(ax=ax, **rain_keywords)
        ax.add_patch(dipole.as_patch(color='blue'))
        ax.set_title('December {}'.format(yr))

        # JANUARY
        ax = axes[2, i]
        selector = lambda ds: ds.sel(time = slice('{}-01-01'.format(yr), '{}-01-31'.format(yr+1))).mean(dim='time')
        rain_sub = selector(rain)
        sst_sub = selector(sea_temp)
        sst_sub.plot.contourf(ax=ax, **sst_keywords)
        rain_sub.plot.contourf(ax=ax, **rain_keywords)
        ax.add_patch(dipole.as_patch(color='blue'))
        ax.set_title('January {}'.format(yr+1))

        # FEBRUARY
        ax = axes[3, i]
        selector = lambda ds: ds.sel(time = slice('{}-02-01'.format(yr), '{}-02-28'.format(yr+1))).mean(dim='time')
        rain_sub = selector(rain)
        sst_sub = selector(sea_temp)
        sst_sub.plot.contourf(ax=ax, **sst_keywords)
        rain_sub.plot.contourf(ax=ax, **rain_keywords)
        ax.add_patch(dipole.as_patch(color='blue'))
        ax.set_title('February {}'.format(yr+1))

    # Format axes
    viz.format_axes(
        axes, extent = None, border=True,
        xticks=np.linspace(-180, 180, 19), yticks=np.linspace(-90, 90, 10)
    )
    for ax in axes.flat:
        ax.set_xlim([-100, 75]) # is relative to central longitude
        ax.set_ylim([-60, 10])
    
    # Add plot labels
    letters = string.ascii_lowercase
    for i, ax in enumerate(axes.flat):
        label = '({})'.format(letters[i])
        t = ax.text(0.05, 0.9, label, fontsize=11, transform=ax.transAxes)
        t.set_bbox(dict(facecolor='white', edgecolor='gray'))

    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
