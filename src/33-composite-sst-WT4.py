import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import cartopy.crs as ccrs
import cartopy.feature
import os

import pyfloods.visualize as viz
from pyfloods import paths,region
from pyfloods.raw_data import sst

savefigs = True
map_proj = ccrs.PlateCarree(central_longitude=-100)
data_proj = ccrs.PlateCarree()

wt = xr.open_dataarray(paths.file_weather_types).to_dataframe(name='wtype')
wt['T'] = wt.index.to_period("M")
wt = wt.groupby(['T', 'wtype']).size().unstack()
wt.sort_values(4, ascending=False).head()

sea_temp = sst.get_data()

n_months = 15
times = wt.sort_values(4, ascending=False).head(n_months).index.to_timestamp()
composite_wt4 = sea_temp.sel(T = np.in1d(sea_temp['T'], times)).mean(dim='T')

dipole = region.Region(lon=[-30,-10], lat=[-20,-50])

# MAKE PLOT
fig, ax = plt.subplots(nrows=1, ncols=1, subplot_kw={'projection': map_proj},
                       figsize=(16, 5))
composite_wt4.plot.contourf(
    ax=ax, transform=data_proj,
    levels=np.linspace(-0.6, 0.6, 13),
    cmap='PuOr_r',
    cbar_kwargs={'label': 'SST Anomaly [Degrees C]'}, extend='both'
)
ax.add_patch(dipole.as_patch(color='black'))
viz.FormatAxes(
    ax, coast=True, grid=False, border=True, river = False,
    ticks=[np.linspace(-180, 180, 19), np.linspace(-90, 90, 19)]
)
ax.set_xlim([-120, 120])
ax.set_ylim([-70, 15])
fig.savefig(os.path.join(paths.figures, 'ssta-composite-wt4.pdf'), bbox_inches='tight')
