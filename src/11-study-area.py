import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature
import pandas as pd
from cartopy.io import shapereader
import matplotlib.patches as patches
import os.path

from pyfloods import region,paths,raw_data
import pyfloods.visualize as viz

# Figure Options
map_proj = ccrs.PlateCarree()
data_proj = ccrs.PlateCarree()

rivers = shapereader.natural_earth(
    category='physical',
    name='rivers_lake_centerlines',
    resolution='10m'
)
rivers = shapereader.Reader(rivers)

# Station Descriptions
desc = pd.read_csv(paths.file_station_description)

# Elevation
elev = raw_data.topo.get_data().sel(X=slice(-85, -32.5), Y=slice(-50,15))
log_elev = np.log10(elev)

# Create the plot!
fig, axes = plt.subplots(nrows=1, ncols=2, subplot_kw={'projection': map_proj}, figsize=[10, 7.5])
ax = axes[0]
log_elev.plot(ax=ax, transform=data_proj, add_colorbar=False, add_labels=False, vmin=-0.5, vmax=4, cmap='terrain')
ax.add_patch(region.wtype.as_patch(label='Weather Typing Region', color='blue'))
ax.add_patch(region.lower_py_river.as_patch(label='Lower PY River Basin', color='red'))
ax.legend(loc='lower right')

ax = axes[1]
C = log_elev.plot(ax=ax, transform=data_proj, add_colorbar=False, add_labels=False, vmin=-0.5, vmax=4, cmap='terrain')
ax.add_patch(region.lower_py_river.as_patch(label='Lower PY River Basin', color='red'))

rivernum_plot = [36, 1032, 1125, 294]
for rec in rivers.records():
    name = rec.attributes['name']
    num = rec.attributes['rivernum']
    if np.in1d(num, rivernum_plot):
        ax.add_geometries( [rec.geometry], ccrs.PlateCarree(), edgecolor='blue', facecolor='none')
    pass
for i in range(desc.shape[0]):
    ax.scatter(x=desc['lon'][i], y = desc['lat'][i], color='k')
    ax.text(x=desc['lon'][i] + 0.25, y = desc['lat'][i] - 0.1, s = desc['short_name'][i], color='black')
ax.legend(loc = 'upper left')

viz.FormatAxes(axes[0], coast=True, grid=True, border=True,
           extent = [-85, -32.5, -50, 15], ticks=[np.linspace(-180, 180, 37), np.linspace(-90, 90, 19)])
viz.FormatAxes(axes[1], coast=True, grid=True, border=True,
           extent = [-67.5, -52.5, -30, -12.5], ticks=[np.linspace(-180, 180, 73), np.linspace(-90, 90, 37)])
plt.tight_layout()
fig.subplots_adjust(right=0.9)

cax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
cb = plt.colorbar(C, cax=cax)
cb.set_label(r"$\log_{10}$ Elevation [m]", rotation=270)
cb.ax.get_yaxis().labelpad = 20

fig.savefig(os.path.join(paths.figures, 'study-area.jpg'), bbox_inches='tight', dpi=500)
