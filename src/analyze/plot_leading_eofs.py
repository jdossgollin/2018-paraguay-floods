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
from sklearn.decomposition import PCA
import string

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--psi_wtype", help="The streamfunction over the weather typing region")
parser.add_argument("--n_eof", type=int)

def main():
    # Read in raw data
    args = parser.parse_args()
    psi = xr.open_dataset(args.psi_wtype)['anomaly']
    psi_stacked = psi.stack(grid=['lon', 'lat'])

    # Carry out PCA
    pca = PCA(n_components=args.n_eof).fit(psi_stacked)
    loadings = pca.components_

    # Convert to xarray
    loadings = xr.DataArray(
        loadings, coords={
            'eof': np.arange(args.n_eof)+1, 'grid': psi_stacked.coords.get('grid')
        }, dims=['eof', 'grid']
    ).unstack('grid')

    # Plot Options
    aspect = (loadings.lon.max() - loadings.lon.min()) / (loadings.lat.max() - loadings.lat.min())
    data_proj = ccrs.PlateCarree()
    map_proj = ccrs.PlateCarree()

    # Plot the loadings
    p = loadings.plot.contourf(
        x='lon', y='lat',
        transform=data_proj,
        col='eof',
        aspect=aspect,
        subplot_kws={'projection': data_proj},
        cmap='PuOr',
        levels=np.linspace(-0.3, 0.3, 13)
    )

    # Add stuff to the axes
    extent = [loadings.lon.values.min(), loadings.lon.values.max(), loadings.lat.values.min(), loadings.lat.values.max()]
    viz.format_axes(
        p.axes,
        coast=True, grid=False, border=True,
        xticks=np.linspace(-180, 180, 91), yticks=np.linspace(-90, 90, 37),
        extent=extent,
        crs = data_proj,
    )
    for i,ax in enumerate(p.axes.flat):
       ax.set_title('EOF {}'.format(i+1))

    # Add plot labels
    letters = string.ascii_lowercase
    for i, ax in enumerate(p.axes.flat):
        label = '({})'.format(letters[i])
        t = ax.text(0.05, 0.9, label, fontsize=11, transform=ax.transAxes)
        t.set_bbox(dict(facecolor='white', edgecolor='gray'))

    # Save figure
    plt.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
