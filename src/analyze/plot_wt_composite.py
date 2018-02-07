#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot Weather Type composites
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import colorcet as cc
import datetime

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--wt", help="The weather type data")
parser.add_argument("--psi", help="The streamfunction data file")
parser.add_argument("--rain", help="The rainfall data file")

def main():
    """Run everything
    """
    args = parser.parse_args()
    psi = xr.open_dataset(args.psi)
    prcp = xr.open_dataset(args.rain)
    w_type = xr.open_dataarray(args.wt).to_dataframe(name='wtype')

    # Plot Options
    map_proj = ccrs.Orthographic(-60, -10)
    data_proj = ccrs.PlateCarree()
    wt_unique = np.unique(w_type['wtype'])
    figsize = (18, 4.5)

    # Get the proportion of weather types each day
    wt_counts = w_type.groupby('wtype').size().div(w_type['wtype'].size)

    # Set up the Figure
    fig, axes = plt.subplots(nrows=2, ncols=len(wt_unique), subplot_kw={'projection': map_proj}, figsize=figsize)

    # Loop through
    for i,w in enumerate(wt_unique):
        def selector(ds):
            times = w_type.loc[w_type['wtype'] == w].index
            ds = ds.sel(time = np.in1d(ds.time, times))
            ds = ds.mean(dim = 'time')
            return(ds)

        # Top row: streamfunction anomalies
        ax = axes[0, i]
        ax.set_title('WT {}: {:.1%} of days'.format(w, wt_counts.values[i]))
        C0 = selector(psi['anomaly']).plot.contourf(
            transform = data_proj,
            ax=ax,
            cmap = cc.cm['coolwarm'],
            extend="both",
            levels=12,
            add_colorbar=False,
            add_labels=False
        )
        #ax.add_patch(region.wtype.as_patch(color='black'))
        # Bottom row: rainfall anomalies
        ax = axes[1, i]
        C1 = selector(prcp['anomaly']).plot.contourf(
            transform = data_proj,
            ax=ax,
            cmap = 'BrBG',
            extend="both",
            levels=np.linspace(-6, 6, 13),
            add_colorbar=False,
            add_labels=False
        )
        #ax.add_patch(region.wtype.as_patch(color='black'))

    # Add Colorbar
    plt.tight_layout()
    fig.subplots_adjust(right=0.94)
    cax0 = fig.add_axes([0.97, 0.55, 0.0075, 0.35])
    cax1 = fig.add_axes([0.97, 0.05, 0.0075, 0.4])
    cbar0 = fig.colorbar(C0, cax = cax0)
    cbar0.formatter.set_powerlimits((4, 4))
    cbar0.update_ticks()
    cbar0.set_label(r'$\psi_{850}$ Anomaly [$m^2$/s]', rotation=270)
    cbar0.ax.get_yaxis().labelpad = 20
    cbar1 = fig.colorbar(C1, cax=cax1)
    cbar1.set_label('Precip. Anomaly [mm/d]', rotation=270)
    cbar1.ax.get_yaxis().labelpad = 20

    # Format these axes
    southern_hemisphere = Region(lon = [-120, 0], lat = [-50, 5])
    south_america = Region(lon = [-85, -30], lat = [-40, -7.5])
    viz.format_axes(axes[0,:], extent = southern_hemisphere.as_extent(), border=True)
    viz.format_axes(axes[1,:], extent = south_america.as_extent(), border=True)

    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
