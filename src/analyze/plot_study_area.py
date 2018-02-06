#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download a single year of 6-Hour Reanalysis V2 data from
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io import shapereader
import colorcet as cc

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--LPRX0", type=float)
parser.add_argument("--LPRX1", type=float)
parser.add_argument("--LPRY0", type=float)
parser.add_argument("--LPRY1", type=float)
parser.add_argument("--WTX0", type=float)
parser.add_argument("--WTX1", type=float)
parser.add_argument("--WTY0", type=float)
parser.add_argument("--WTY1", type=float)

def plot_rivers(ax):
    """Get the rivers and add them to a matplotlib axis
    """
    rivernum_plot = [36, 1032, 1125, 294]
    rivers = rivers = shapereader.natural_earth(
        category='physical',
        name='rivers_lake_centerlines',
        resolution='10m'
    )
    rivers = shapereader.Reader(rivers)
    for rec in rivers.records():
        num = rec.attributes['rivernum']
        if np.in1d(num, rivernum_plot):
            ax.add_geometries(
                [rec.geometry], crs=ccrs.PlateCarree(),
                edgecolor='blue', facecolor='none'
            )

def plot_stations(ax):
    desc = pd.read_csv('data/raw/station_description.csv')
    for i in range(desc.shape[0]):
        ax.scatter(x=desc['lon'][i], y = desc['lat'][i], color='k')
        ax.text(x=desc['lon'][i] + 0.25, y = desc['lat'][i] - 0.1, s = desc['short_name'][i], color='black')


def main():
    """Run everything
    """
    args = parser.parse_args()

    # Create Region objects from the tangle of input arguments
    lprb_region = Region(lon=[args.LPRX0, args.LPRX1], lat=[args.LPRY0, args.LPRY1])
    wt_region = Region(lon=[args.WTX0, args.WTX1], lat=[args.WTY0, args.WTY1])

    # Read in raw data
    elev = xr.open_dataarray('data/external/elevation.nc').sel(
        X=slice(-85, -32.5),
        Y=slice(-50, 15)
    )
    elev = np.log10(elev)

    # Plotting Options
    map_proj = ccrs.PlateCarree()
    data_proj = ccrs.PlateCarree()
    elev_cmap = cc.cm['bgyw']
    elev_min = -0.3
    elev_max = 3.7
    contours = np.linspace(elev_min, elev_max, 21)
    levels = np.linspace(elev_min, elev_max, 41)
    figsize = (10, 7.5)

    # Create the figure and axes
    fig, axes = plt.subplots(nrows=1, ncols=2, subplot_kw={'projection': map_proj}, figsize=figsize)

    # Add stuff to first subplot
    ax = axes[0]
    C = elev.plot.contourf(ax=ax, transform=data_proj, add_colorbar=False, add_labels=False, levels=levels, cmap=elev_cmap)
    ax.add_patch(wt_region.as_patch(label='Weather Typing Region', color='blue'))
    ax.add_patch(lprb_region.as_patch(label='Lower PY River Basin', color='red'))
    ax.legend(loc='lower right')
    viz.format_axes(
        ax, coase=True, grid=True, river=False, border=True,
        extent=[-85, -32.5, -50, 15], crs=data_proj,
        xticks=np.linspace(-180, 180, 37), yticks=np.linspace(-90, 90, 19)
    )

    # Add stuff to second subplot
    ax = axes[1]
    C = elev.plot.contourf(ax=ax, transform=data_proj, add_colorbar=False, add_labels=False, levels=levels, cmap=elev_cmap)
    elev.plot.contour(ax=ax, transform=data_proj, add_colorbar=False, add_labels=False, colors='k', levels=contours, alpha=0.3, linewidths=0.4)
    ax.add_patch(lprb_region.as_patch(label='Lower PY River Basin', color='red'))
    plot_rivers(ax=ax)
    plot_stations(ax=ax)
    viz.format_axes(
        ax, coase=True, grid=True, river=False, border=True,
        extent=[-65, -52.5, -30, -15], crs=data_proj,
        xticks=np.linspace(-180, 180, 73), yticks=np.linspace(-90, 90, 37)
    )
    ax.legend(loc='upper left')

    # Add color bar
    fig.tight_layout()
    fig.subplots_adjust(right=0.9)
    cax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
    cb = plt.colorbar(C, cax=cax)
    cb.set_label(r"$\log_{10}$ Elevation [m]", rotation=270)
    cb.ax.get_yaxis().labelpad = 20

    # Save to file
    fig.savefig(args.outfile, bbox_inches='tight', dpi=500)

if __name__ == "__main__":
    main()
