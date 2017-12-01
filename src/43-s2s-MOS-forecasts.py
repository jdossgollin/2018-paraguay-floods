import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os

from pyfloods import visualize as viz # custom plotting library
from pyfloods import paths

obs_url = 'http://iridl.ldeo.columbia.edu/home/.agmunoz/.Paraguay/.Obs/.Obsrain_90thpctl/dods'
obs_exceed = xr.open_dataarray(obs_url)
obs_exceed = obs_exceed.isel(T=(obs_exceed['T'].size - 1))
hatch0 = np.ma.masked_invalid(obs_exceed.values)
hatch = np.ma.masked_less(hatch0, 0.9)
Xh, Yh = np.meshgrid(obs_exceed.X, obs_exceed.Y)

model_names = ['Raw', 'XLR', 'HXLR', 'PCR', 'CCA']

def get_forecast(model, type):
    base_url = 'http://iridl.ldeo.columbia.edu/ds%3A/home/.agmunoz/.Paraguay/'
    url = base_url + '{}/'.format(model)
    if type == 'forecast':
        url += '.Odds_1-7Dec2015/dods'
    elif type == 'skill':
        url += '.2AFCProbFcsts/dods'
    elif type == 'ignorance':
        url += '.IGNProbFcsts/dods'
    else:
        raise ValueError('type is not valid')
    ds = xr.open_dataarray(url)
    ds = ds.sortby(['X', 'Y']) # be more consistent
    if ds.ndim > 2:
        ds = ds.isel(time=0).drop('time')
    ds.coords['model'] = model
    return(ds)

ncols = len(model_names)
fig, axes = plt.subplots(
    ncols=len(model_names), nrows=3,
    subplot_kw={'projection': ccrs.PlateCarree()},
    figsize=(14,10), sharex=True, sharey=True
)
for i,m in enumerate(model_names):
    ax = axes[0, i] # Forecast for December 1-7 2015
    ax.set_title(m)
    ds = get_forecast(model=m, type='forecast')
    X,Y = np.meshgrid(ds.X, ds.Y)
    sub = ds.values
    sub = np.ma.masked_invalid(sub)
    sub = np.ma.masked_less(sub, 0)
    C1 = ax.pcolormesh(X, Y, sub, cmap="terrain_r", transform=ccrs.PlateCarree(), vmin=0, vmax=8)
    ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')

    ax = axes[1, i] # Ignorance Score
    ds = get_forecast(model=m, type='ignorance')
    X,Y = np.meshgrid(ds.X, ds.Y)
    sub = ds.values
    sub = np.ma.masked_invalid(sub)
    sub = np.ma.masked_less(sub, 0)
    C2 = ax.pcolormesh(X, Y, sub, transform=ccrs.PlateCarree(), cmap="terrain_r", vmin=0, vmax=2.5)
    ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')

    ax = axes[2, i] # 2AFC Skill Score
    ds = get_forecast(model=m, type='skill')
    X,Y = np.meshgrid(ds.X, ds.Y)
    sub = ds.values
    sub = np.ma.masked_invalid(sub)
    sub = np.ma.masked_less(sub, 0)
    C3 = ax.pcolormesh(X, Y, sub, transform=ccrs.PlateCarree(), cmap="PuOr", vmin=0, vmax=100)
    ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')

viz.FormatAxes(axes, ticks=[np.linspace(-180, 180, 73), np.linspace(-90, 90, 37)],
               extent = [np.min(X), np.max(X), np.min(Y), np.max(Y)])

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

fig.savefig(os.path.join(paths.figures, 's2s-forecast-mos.pdf'), bbox_inches="tight")
