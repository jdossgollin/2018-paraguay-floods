#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download a single year of 6-Hour Reanalysis V2 data from
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""

import argparse
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import colorcet as cc

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--wt", help="The Weather Type sequence")

def main():
    # Read in data
    args = parser.parse_args()
    wt = xr.open_dataarray(args.wt).to_dataframe()

    # Get the adjusted year and day of season
    time = wt.index
    year = time.year
    month = time.month
    year_adj = time.year.values
    year_adj[np.in1d(month, [11, 12])] += 1
    wt['year_adj'] = year_adj
    wt['doy'] = wt.groupby(year_adj).transform(lambda x: np.arange(x.size))['year_adj']

    # Make klee diagram and annual proportion diagram
    wt_ds = wt.set_index(['doy', 'year_adj']).to_xarray()['wtype']
    wt_prop = wt.groupby(['year_adj', 'wtype']).size().to_xarray()
    wt_prop = wt_prop / wt_prop.sum(dim='wtype')
    wt_prop = wt_prop.to_pandas()

    # set up the figure
    fig,axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    ax = axes[0]
    wt_ds.plot(x='doy', y='year_adj', ax=ax, add_colorbar=False)
    ax.set_xlabel('Days Since 01 November')
    ax.set_ylabel('Year')
    ax = axes[1]
    wt_prop.plot.barh(stacked=True, cmap='viridis', ax=ax)
    ax.set_xlabel('Proportion of Days')
    ax.set_ylabel('')
    ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
