import xarray as xr
import pandas as pd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import os

import pyfloods.visualize as viz
import pyfloods.paths
from pyfloods.anomalies import rainfall

df = pd.read_csv(
    os.path.join(pyfloods.paths.data_raw, 'SeasonalForecast.tsv'),
    skiprows=2, delim_whitespace=True,
    names=['lon', 'lat', 'prob_exceed'],
    index_col=['lat', 'lon'])['prob_exceed'].to_xarray()

prcp = rainfall.get_data().sel(
    lon=slice(df.lon.min(), df.lon.max()),
    lat=slice(df.lat.min(), df.lat.max()))['raw']
prcp = prcp.sel(time = prcp['time.season'] == 'DJF')
prcp_year = prcp.groupby('year_adj').mean(dim='time')
prcp_q90 = prcp_year.quantile(0.90, dim='year_adj')
prcp_exceed = prcp_year.sel(year_adj=2016) > prcp_q90

X,Y = np.meshgrid(df.lon, df.lat)
Xh,Yh = np.meshgrid(prcp_exceed.lon, prcp_exceed.lat)
hatch = np.ma.masked_invalid(prcp_exceed.values)
hatch = np.ma.masked_less(hatch, True)

# MAKE PLOT
fig, ax = viz.SetupAxes(figsize=(5.5,8), ncol=1, nax=1,proj=ccrs.PlateCarree())
fig.subplots_adjust(right=0.925)
cax1 = fig.add_axes([0.95, 0.15, 0.035, 0.7])
sub = np.ma.masked_invalid((df/(1-df)) / (.1/(1-.1)))
C = ax.pcolormesh(X,Y, sub, transform=ccrs.PlateCarree(),
                  cmap="terrain_r", vmin=0, vmax=7)
ax.pcolor(Xh, Yh, hatch, facecolor='none', edgecolors='k')
cb = plt.colorbar(C, cax=cax1)
cb.set_label("Odds Ratio", rotation=270)
cb.ax.get_yaxis().labelpad = 15
viz.FormatAxes(ax, ticks=[np.linspace(-180, 180, 73), np.linspace(-90, 90, 37)],
               extent = [np.min(X), np.max(X), np.min(Y), np.max(Y)])

fig.savefig(os.path.join(pyfloods.paths.figures, 'seasonal-forecast.pdf'), bbox_inches='tight')
