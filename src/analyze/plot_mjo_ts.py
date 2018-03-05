#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot the MJO Time Series
"""

import argparse
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import colorcet as cc

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--mjo", help="The MJO Data")

def main():
    # Read in raw data
    args = parser.parse_args()
    mjo = xr.open_dataset(args.mjo).sel(time=slice('2015-12-01', '2016-02-29'))
    dt = np.arange(mjo['time'].size)

    # Set up axes
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8.5, 6.5))

    # Add lines and circles for MJO phases
    ax.axvline(0, c='gray')
    ax.axhline(0, c='gray')
    ax.plot([-100, 100], [-100, 100], c='gray')
    ax.plot([-100, 100], [100, -100], c='gray')
    circle = plt.Circle((0, 0), 1, color='gray', fill=False)
    ax.add_artist(circle)

    # Plot MJO
    ax.plot(mjo['RMM1'], mjo['RMM2'], c='gray')
    C = ax.scatter(mjo['RMM1'], mjo['RMM2'], c=dt, cmap=cc.cm['inferno'], s=45)
    
    # Set up axes
    ax.set_aspect('equal')
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    plt.colorbar(C, label='Days Since 2015-11-01')
    ax.set_xlabel('MJO RMM1')
    ax.set_ylabel('MJO RMM2')

    # Annotate phases
    for phase in np.arange(1, 9):
        theta = np.pi * 7/8 + np.pi * phase / 4 
        radius = 3
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        ax.text(x, y, phase, fontsize=12)

    # Save
    fig.tight_layout()
    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
