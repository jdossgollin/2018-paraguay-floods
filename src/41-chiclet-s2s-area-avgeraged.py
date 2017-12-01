import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os.path

from pyfloods import visualize as viz
from pyfloods import paths,region
from pyfloods.raw_data import s2s
from pyfloods.anomalies import rainfall
from pyfloods.region import lower_py_river as lpr

modeled = s2s.get_data()
modeled['S'] = pd.to_datetime(modeled['S'].values).date
modeled['S'] = pd.to_datetime(modeled['S'].values)
modeled['L'] = np.int_(modeled['L'].astype('timedelta64[D]') / np.timedelta64(1, 'D'))
modeled = modeled.to_dataframe().dropna()
modeled = modeled.reset_index()
modeled['target_date'] = modeled['S'] + modeled['L'].apply(np.ceil).apply(lambda x: pd.Timedelta(x, unit='D'))
modeled = modeled.loc[np.logical_and(modeled['target_date'] >= '2015-11-01', modeled['target_date'] <= '2016-02-29')]
modeled = modeled.set_index(['target_date', 'L', 'M'])

obs = rainfall.get_data()['raw'].sel(
    lon = slice(lpr.lonmin, lpr.lonmax),
    lat = slice(lpr.latmin, lpr.latmax)).mean(dim=['lon', 'lat']).to_pandas()
climatology = np.mean(obs)

modeled['tpa'] = modeled['tp'] - climatology
forecast = modeled.to_xarray()['tpa'].mean(dim='M')
ft, fl = np.meshgrid(np.arange(forecast.target_date.size), forecast.L.values)
target_date = pd.to_datetime(forecast.target_date.values)
obs = obs['2015-11-01':'2016-02-29']

# MAKE PLOT
fig,axes = plt.subplots(ncols=1, nrows=2, figsize=((15,8)), gridspec_kw = {'height_ratios':[3, 1]})

ax=axes[0] # Chiclet
C1 = forecast.plot.pcolormesh(x='target_date', y='L', cmap = 'BrBG', ax=ax, add_colorbar=False, add_labels=False)
ax.set_ylabel("Lead Time (Days)")
ax.set_xticks([])
current_x_lim = ax.get_xlim()
ax.grid(True)

ax = axes[1] # Observed Rainfall
obs.plot(ax=ax)
ax.grid(True)
ax.set_ylim(0, 40)
ax.invert_yaxis()
ax.set_ylabel("Rainfall [mm/day]")

fig.tight_layout()
fig.subplots_adjust(right=0.94)
cax = fig.add_axes([0.97, 0.4, 0.01, 0.55])
cbar = fig.colorbar(C1, cax = cax)
cbar.set_label("Ensemble-Mean Rainfall Forecast [mm/day]", rotation=270)
cbar.ax.get_yaxis().labelpad = 20
fig.savefig(os.path.join(paths.figures, 'chiclet-s2s-area-averaged.pdf'), bbox_inches="tight")
