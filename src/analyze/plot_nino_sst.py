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

    sea_temp = xr.open_dataarray(args.sst).rename({'X': 'lon', 'Y': 'lat', 'T': 'time'})
    sea_temp = sea_temp.sel(time = np.in1d(sea_temp['time.month'], [11, 12, 1, 2]))
    
    nino_times = pd.to_datetime(['1982-12-01', '1997-12-01', '2015-12-01'])
    sst_plot = sea_temp.sel(time=np.in1d(sea_temp['time'], nino_times))

    # Plot options
    map_proj = ccrs.PlateCarree(central_longitude=-60)
    data_proj = ccrs.PlateCarree()
    figsize = (10, 9)
    dipole = Region(lon=[-30,-10], lat=[-10,-40])

    cmap = cc.cm['coolwarm']
    p = sst_plot.plot.contourf(
       x='lon', y='lat',
       transform=data_proj,
       col='time',
       col_wrap=1,
       subplot_kws={'projection': map_proj},
       cmap=cmap,
       levels=np.linspace(-3.5, 3.5, 15),
       figsize=figsize
    )

    # Add stuff to the axes
    viz.format_axes(
        p.axes,
        coast=True, grid=False, border=True,
        xticks=np.linspace(-180, 180, 19), yticks=np.linspace(-90, 90, 10)
    )

    dipole = Region(lon=[-30,-10], lat=[-10,-40])
    for ax in p.axes.flat:
        ax.set_xlim([-80, 80]) 
        ax.set_ylim([-60, 10])
        ax.add_patch(dipole.as_patch(color='black'))

    # Add plot labels
    letters = string.ascii_lowercase
    for i, ax in enumerate(p.axes.flat):
        label = '({})'.format(letters[i])
        t = ax.text(0.05, 0.9, label, fontsize=11, transform=ax.transAxes)
        t.set_bbox(dict(facecolor='white', edgecolor='gray'))

    plt.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
