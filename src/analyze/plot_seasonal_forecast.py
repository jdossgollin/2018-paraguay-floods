#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot the seasonal forecast from IRI
"""

import argparse
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import colorcet as cc

from region import Region
import visualize as viz

parser = argparse.ArgumentParser()
parser.add_argument("--rain", help="The rainfall data file")
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--seasonal", help="The seasonal forecast file")

def main():
    """Run everything
    """
    args = parser.parse_args()
    df = pd.read_csv(
        args.seasonal,
        skiprows=2, delim_whitespace=True,
        names=['lon', 'lat', 'prob_exceed'],
        index_col=['lat', 'lon']
    )['prob_exceed'].to_xarray()
    prcp = xr.open_dataset(args.rain).sel(
        lon=slice(df.lon.min(), df.lon.max()),
        lat=slice(df.lat.min(), df.lat.max())
    )['raw']
    prcp = prcp.sel(time = prcp['time.season'] == 'DJF')
    prcp_year = prcp.groupby('year_adj').mean(dim='time')
    prcp_q90 = prcp_year.quantile(0.90, dim='year_adj')
    prcp_exceed = prcp_year.sel(year_adj=2016) > prcp_q90

    X,Y = np.meshgrid(df.lon, df.lat)
    Xh,Yh = np.meshgrid(prcp_exceed.lon, prcp_exceed.lat)
    hatch = np.ma.masked_invalid(prcp_exceed.values)
    hatch = np.ma.masked_less(hatch, True)

    # MAKE PLOT
    fig, ax = plt.subplots(
        nrows=1, ncols=1, figsize=(5.5, 8),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    sub = np.ma.masked_invalid((df/(1-df)) / (.1/(1-.1)))
    C = ax.pcolormesh(X,Y, sub, transform=ccrs.PlateCarree(),
                    cmap=cc.cm['bgyw_r'], vmin=0, vmax=7)
    ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k', linewidth=1)

    viz.format_axes(
        ax, border=True, extent = [np.min(X), np.max(X), np.min(Y), np.max(Y)],
        xticks=np.linspace(-180, 180, 73), yticks=np.linspace(-90, 90, 37)
    )

    fig.subplots_adjust(right=0.925)
    cax1 = fig.add_axes([0.95, 0.15, 0.035, 0.7])
    cb = plt.colorbar(C, cax=cax1)
    cb.set_label("Odds Ratio", rotation=270)
    cb.ax.get_yaxis().labelpad = 15

    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
