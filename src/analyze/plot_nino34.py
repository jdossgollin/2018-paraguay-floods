#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot the NINO 3.4 Time Series
"""

import argparse
import xarray as xr
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--nino", help="The NINO 3.4 Data")

def main():
    # Read in raw data
    args = parser.parse_args()
    nino = xr.open_dataarray(args.nino)

    # Set up figure
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 3.5))

    # Plot full time series on left hand side
    nino.plot(ax=ax, c='blue')

    # Plot Study Time with Dots
    nino.sel(time=slice('2015-11-01', '2016-02-01')).plot(ax=ax, marker='o', c='blue')

    # Label Axes
    ax.set_xlabel('Time')
    ax.set_ylabel('NINO 3.4 Index')

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
