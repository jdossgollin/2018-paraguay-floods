#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download a single year of 6-Hour Reanalysis V2 data from
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""

import argparse
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import colorcet as cc
from sklearn.decomposition import PCA

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--prcp_rpy", help="The Paraguay River Basin Rainfall")
parser.add_argument("--wt", help="The Weather Type sequence")

def main():
    # Read in raw data
    args = parser.parse_args()
    prcp_rpy = xr.open_dataset(args.prcp_rpy)['raw'].to_dataframe()
    wt = xr.open_dataarray(args.wt).to_dataframe(name='wtype')
    wt_prcp = prcp_rpy.join(wt['wtype']).dropna()
    wt_prcp = wt_prcp['2015-11-01':'2016-02-29']

    # Get the weather types and rain to plot
    time = wt_prcp.index
    rain = wt_prcp.raw.values
    wt_vec = np.int_(wt_prcp.wtype.values)

    # Plot options
    colors = plt.get_cmap('Accent', 7).colors[1:]
    #plt.style.use('ggplot')
    plt.style.use('seaborn-white')
    figsize=(10, 3.5)

    # Make the plot
    fig,ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
    wt_prcp['raw'].plot(ax=ax, c='gray')
    ax.axhline(prcp_rpy.raw.quantile(0.50), label="p50", color='blue', linestyle='--', linewidth=0.75)
    ax.axhline(prcp_rpy.raw.quantile(0.90), label="p90", color='blue', linestyle='--', linewidth=0.75)
    ax.axhline(prcp_rpy.raw.quantile(0.99), label="p99", color='blue', linestyle='--', linewidth=0.75)
    ax.set_ylabel('Area-Averaged Rainfall [mm/d]')
    ax.set_xlabel('')

    # Annotate with WT labels
    for i,t in enumerate(time):
        ax.text(t, rain[i], '{:d}'.format(wt_vec[i]), color=colors[wt_vec[i]-1], size=11, weight='bold')

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
