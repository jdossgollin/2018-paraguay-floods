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
from sklearn.decomposition import PCA
import cartopy.crs as ccrs
import cartopy.feature
import colorcet as cc
import string

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the figure to save")
parser.add_argument("--psi_wtype", help="The streamfunction over the weather typing region")
parser.add_argument("--sst", help="The SST anomaly data")
parser.add_argument("--n_eof", type=int)
parser.add_argument("--WTX0", type=float)
parser.add_argument("--WTX1", type=float)
parser.add_argument("--WTY0", type=float)
parser.add_argument("--WTY1", type=float)

def covariance_gufunc(x, y):
    cov = (
        (x - x.mean(axis=-1, keepdims=True)) * (y - y.mean(axis=-1, keepdims=True))
    ).mean(axis=-1)
    return cov

def pearson_correlation_gufunc(x, y):
    return covariance_gufunc(x, y) / (x.std(axis=-1) * y.std(axis=-1))

def pearson_correlation(x, y, dim):
    rho = xr.apply_ufunc(
        pearson_correlation_gufunc, x, y,
        input_core_dims=[[dim], [dim]],
        dask='parallelized',
        output_dtypes=[float]
    )
    return rho

def daily_to_monthly(daily):
    df = pd.DataFrame({'year': daily['time.year'], 'month': daily['time.month'], 'day': 1})
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    daily['time'] = df['date'].values
    monthly = daily.groupby('time').mean(dim='time')
    return monthly

def main():
    """Run everything
    """
    args = parser.parse_args()

    sea_temp = xr.open_dataarray(args.sst).rename({'X': 'lon', 'Y': 'lat', 'T': 'time'})
    sea_temp = sea_temp.sel(time = np.in1d(sea_temp['time.month'], [11, 12, 1, 2])).resample(time='1D').ffill()
    psi = xr.open_dataset(args.psi_wtype)['anomaly']
    psi_stacked = psi.stack(grid=['lon', 'lat'])
    pca = PCA(n_components=args.n_eof).fit(psi_stacked)
    pc_ts = pca.transform(psi_stacked)
    pc_ts = pd.DataFrame(pc_ts, index=psi_stacked['time'])
    pc_ts.columns = ['EOF{}'.format(i) for i in np.arange(1, args.n_eof + 1)]
    pc_ts = pc_ts.to_xarray()
    mrg = xr.merge([sea_temp, pc_ts], join='inner')
    
    corr2 = pearson_correlation(mrg['ssta'], mrg['EOF2'], dim='time')
    corr3 = pearson_correlation(mrg['ssta'], mrg['EOF3'], dim='time')

    # Plot options
    map_proj = ccrs.PlateCarree(central_longitude=-60)
    data_proj = ccrs.PlateCarree()
    figsize = (10, 6.5)
    dipole = Region(lon=[-30,-10], lat=[-15,-40])
    wt_region = Region(lon=[args.WTX0, args.WTX1], lat=[args.WTY0, args.WTY1])


    cmap = cc.cm['coolwarm']

    # Set up 2 plots
    fig, axes = plt.subplots(
        nrows=3, ncols=1, subplot_kw={'projection': map_proj},
        figsize=figsize, sharex=True, sharey=True
    )

    # First Plot: Correlation with EOF 2
    ax = axes[0]
    corr2.name = 'Pearson Correlation'
    C0 = corr2.plot.contourf(
        ax=ax, transform=data_proj,
        cmap=cc.cm['gwv'],
        levels=11,
        add_colorbar=True,
        add_labels=True,
        extend='both',
    )
    ax.add_patch(wt_region.as_patch(color='black'))
    ax.add_patch(dipole.as_patch(color='blue'))
    ax.set_title('')

    # First Plot: Correlation with EOF 3
    ax = axes[1]
    corr3.name = 'Pearson Correlation'
    C1 = corr3.plot.contourf(
        ax=ax, transform=data_proj,
        cmap=cc.cm['gwv'],
        levels=11,
        add_colorbar=True,
        add_labels=True,
        extend='both',
    )
    ax.add_patch(wt_region.as_patch(color='black'))
    ax.add_patch(dipole.as_patch(color='blue'))
    ax.set_title('')

    # Second: Plot December 2015
    ax = axes[2]
    sub2 = sea_temp.sel(time = '2015-12-01')
    sub2.name = 'SSTA [degree C]'
    C2 = sub2.plot.contourf(
        ax=ax, transform=data_proj,
        cmap=cmap,
        levels=np.linspace(-3.5, 3.5, 15),
        extend='both',
        add_colorbar=True,
        add_labels=True
    )
    ax.add_patch(wt_region.as_patch(color='black'))
    ax.add_patch(dipole.as_patch(color='blue'))
    ax.set_xlim([-120, 120])
    ax.set_ylim([-70, 0])
    ax.set_title('')

    # Format axes
    viz.format_axes(
        axes, extent = None, border=True,
        xticks=np.linspace(-180, 180, 19), yticks=np.linspace(-90, 90, 10)
    )
    for ax in axes.flat:
        ax.set_xlim([-80, 80]) # is relative to central longitude
        ax.set_ylim([-60, 10])

    fig.tight_layout()

    # Add plot labels
    letters = string.ascii_lowercase
    for i, ax in enumerate(axes.flat):
        label = '({})'.format(letters[i])
        t = ax.text(0.05, 0.9, label, fontsize=11, transform=ax.transAxes)
        t.set_bbox(dict(facecolor='white', alpha=0.75, edgecolor='gray'))

    fig.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
