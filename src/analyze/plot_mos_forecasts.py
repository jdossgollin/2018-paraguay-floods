#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MOS Plots
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io import shapereader
import colorcet as cc
import string

from region import Region
import visualize as viz

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")

import visualize as viz

def get_forecast(model, ftype):
    base_url = 'http://iridl.ldeo.columbia.edu/ds%3A/home/.agmunoz/.Paraguay/'
    url = base_url + '{}/'.format(model)
    if ftype == 'forecast':
        url += '.Odds_1-7Dec2015/dods'
    elif ftype == 'skill':
        url += '.2AFCProbFcsts/dods'
    elif ftype == 'ignorance':
        url += '.IGNProbFcsts/dods'
    else:
        raise ValueError('ftype is not valid')
    ds = xr.open_dataarray(url)
    ds = ds.sortby(['X', 'Y']) # be more consistent
    if ds.ndim > 2:
        ds = ds.isel(time=0).drop('time')
    ds.coords['model'] = model
    return(ds)

def main():
    """Run everything
    """
    args = parser.parse_args()

    obs_url = 'http://iridl.ldeo.columbia.edu/home/.agmunoz/.Paraguay/.Obs/.Obsrain_90thpctl/dods'
    obs_exceed = xr.open_dataarray(obs_url)
    obs_exceed = obs_exceed.isel(T=(obs_exceed['T'].size - 1))
    hatch0 = np.ma.masked_invalid(obs_exceed.values)
    hatch = np.ma.masked_less(hatch0, 0.9)
    Xh, Yh = np.meshgrid(obs_exceed.X, obs_exceed.Y)

    model_names = ['Raw', 'XLR', 'HXLR', 'PCR', 'CCA']

    ncols = len(model_names)
    fig, axes = plt.subplots(
        ncols=len(model_names), nrows=3,
        subplot_kw={'projection': ccrs.PlateCarree()},
        figsize=(11,8), sharex=True, sharey=True
    )
    for i,m in enumerate(model_names):
        ax = axes[0, i] # Forecast for December 1-7 2015
        ax.set_title(m)
        ds = get_forecast(model=m, ftype='forecast')
        X,Y = np.meshgrid(ds.X, ds.Y)
        sub = ds.values
        sub = np.ma.masked_invalid(sub)
        sub = np.ma.masked_less(sub, 0)
        C1 = ax.pcolormesh(X, Y, sub, cmap=cc.cm['inferno'], transform=ccrs.PlateCarree(), vmin=0, vmax=9)
        ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')

        ax = axes[1, i] # Ignorance Score
        ds = get_forecast(model=m, ftype='ignorance')
        X,Y = np.meshgrid(ds.X, ds.Y)
        sub = ds.values
        sub = np.ma.masked_invalid(sub)
        sub = np.ma.masked_less(sub, 0)
        C2 = ax.pcolormesh(X, Y, sub, transform=ccrs.PlateCarree(), cmap=cc.cm['inferno'], vmin=0, vmax=2)
        ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')

        ax = axes[2, i] # 2AFC Skill Score
        ds = get_forecast(model=m, ftype='skill')
        X,Y = np.meshgrid(ds.X, ds.Y)
        sub = ds.values
        sub = np.ma.masked_invalid(sub)
        sub = np.ma.masked_less(sub, 0)
        C3 = ax.pcolormesh(X, Y, sub, transform=ccrs.PlateCarree(), cmap=cc.cm['gwv'], vmin=0, vmax=100)
        ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')

    # Format the axes
    viz.format_axes(
        axes, border=True, extent = [np.min(X), np.max(X), np.min(Y), np.max(Y)],
        xticks=np.linspace(-180, 180, 73), yticks=np.linspace(-90, 90, 37)
    )

    fig.tight_layout()
    fig.subplots_adjust(right=0.94)
    cax1 = fig.add_axes([0.97, 0.7, 0.015, 0.25])
    cax2 = fig.add_axes([0.97, 0.38, 0.015, 0.25])
    cax3 = fig.add_axes([0.97, 0.05, 0.015, 0.25])
    # Color bar for Odds Ratio
    cbar1 = fig.colorbar(C1, cax = cax1)
    cbar1.update_ticks()
    cbar1.set_label(r'Odds Ratio', rotation=270)
    cbar1.ax.get_yaxis().labelpad = 15
    # Color bar for 2AFC
    cbar2 = fig.colorbar(C2, cax=cax2)
    cbar2.set_label(r'Ignorance Score', rotation=270)
    cbar2.ax.get_yaxis().labelpad = 15
    # Color bar for Ignorance
    cbar3 = fig.colorbar(C3, cax=cax3)
    cbar3.set_label(r'2AFC Skill Score', rotation=270)
    cbar3.ax.get_yaxis().labelpad = 15
    
    # Add plot labels
    letters = string.ascii_lowercase
    for i, ax in enumerate(axes.flat):
        label = '({})'.format(letters[i])
        t = ax.text(0.8, 0.1, label, fontsize=12, transform=ax.transAxes)
        t.set_bbox(dict(facecolor='white', alpha=0.75, edgecolor='gray'))
    
    # Save to file
    fig.savefig(args.outfile, bbox_inches='tight', dpi=500)

if __name__ == "__main__":
    main()
