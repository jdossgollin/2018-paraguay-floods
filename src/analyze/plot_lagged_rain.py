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
import datetime
import string

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--rain_rpy", help="The Paraguay River Basin Rainfall")
parser.add_argument("--psi", help="The streamfunction")
parser.add_argument("--rain", help="The streamfunction")
parser.add_argument("--uwnd", help="The zonal wind")
parser.add_argument("--vwnd", help="The meridional wind")

def main():
    """Run everything
    """
    args = parser.parse_args()

    map_proj = ccrs.Orthographic(-60, -10)
    data_proj = ccrs.PlateCarree()
    days_back = [-2, -1, 0, 1]
    figsize = (4 * len(days_back), 4.75)

    psi = xr.open_dataset(args.psi)['anomaly']
    prcp = xr.open_dataset(args.rain)['anomaly']
    uwnd = xr.open_dataset(args.uwnd)['anomaly']
    vwnd = xr.open_dataset(args.vwnd)['anomaly']
    X, Y = np.meshgrid(uwnd.lon, uwnd.lat)
    
    prcp_rpy = xr.open_dataset(args.rain_rpy)['raw'].to_pandas()
    threshold = np.nanpercentile(prcp_rpy, 90)
    rainy_days = prcp_rpy.loc[prcp_rpy > threshold].index
    rainy_days = pd.to_datetime(rainy_days)

    data_proj = ccrs.PlateCarree()
    
    # Initialize the plot and axes
    fig, axes = plt.subplots(nrows=2, ncols=len(days_back), subplot_kw={'projection': map_proj}, figsize=figsize)
    for i,d in enumerate(days_back):

        # define a function to dusbset the data
        def select_fun(ds):
            ds = ds.isel(time = np.in1d(ds.time, rainy_days + datetime.timedelta(days_back[i])))
            ds = ds.mean(dim='time')
            return(ds)

        # Plot the streamfunction
        ax = axes[0, i]
        ax.set_title("t={} d".format(d))

        C0 = select_fun(psi).plot.contourf(
            transform=data_proj, 
            ax=ax,
            cmap='PuOr',
            extend="both",
            levels=np.linspace(-2.5e6, 2.5e6, 11),
            add_colorbar=False, add_labels=False
        )
        # add wind arrows
        U = select_fun(uwnd).values
        V = select_fun(vwnd).values
        magnitude = np.sqrt(U**2 + V**2)
        strongest = magnitude > np.percentile(magnitude, 95)
        ax.quiver(X[strongest], Y[strongest], U[strongest], V[strongest], transform=data_proj, scale=80)

        ax = axes[1, i] # Rainfall
        C1 = select_fun(prcp).plot.contourf(
            transform=data_proj, 
            ax=ax,
            cmap = 'BrBG', extend="both",
            levels = np.linspace(-12, 12, 13),
            add_colorbar=False, add_labels=False
        )

    # set up the axes
    southern_hemisphere = Region(lon = [-120, 0], lat = [-50, 5])
    south_america = Region(lon = [-85, -30], lat = [-40, -7.5])
    viz.format_axes(axes[0,:], extent = southern_hemisphere.as_extent(), border=True)
    viz.format_axes(axes[1,:], extent = south_america.as_extent(), border=True)

    # Add  color bars
    fig.tight_layout()
    fig.subplots_adjust(right=0.935)
    cax0 = fig.add_axes([0.97, 0.55, 0.01, 0.4])
    cax1 = fig.add_axes([0.97, 0.05, 0.01, 0.4])
    cbar0 = fig.colorbar(C0, cax = cax0)
    cbar0.formatter.set_powerlimits((4, 4))
    cbar0.update_ticks()
    cbar0.set_label(r'$\psi_{850}$ Anomaly [$m^2$/s]', rotation=270)
    cbar0.ax.get_yaxis().labelpad = 20
    cbar1 = fig.colorbar(C1, cax=cax1)
    cbar1.set_label('Precip. Anomaly [mm/d]', rotation=270)
    cbar1.ax.get_yaxis().labelpad = 20

    # Add plot labels
    letters = string.ascii_lowercase
    for i, ax in enumerate(axes.flat):
        label = '({})'.format(letters[i])
        t = ax.text(0.025, 0.9, label, fontsize=12, transform=ax.transAxes)
        t.set_bbox(dict(facecolor='white', alpha=0.75, edgecolor='gray'))

    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
