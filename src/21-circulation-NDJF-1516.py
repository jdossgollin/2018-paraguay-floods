import numpy as np
import xarray as xr
import calendar
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

import pyfloods.visualize as viz
from pyfloods.anomalies import rainfall,streamfunction
from pyfloods import region,paths

psi850 = streamfunction.get_data()
psi850 = psi850.sel(time = (psi850['year_adj'] == 2016))['anomaly']
prcp = rainfall.get_data()
prcp = prcp.sel(time = (prcp['year_adj'] == 2016))['anomaly']

map_proj = ccrs.Orthographic(-60, -10)
data_proj = ccrs.PlateCarree()

months_plot = [11, 12, 1, 2]
years_plot = [2015, 2015, 2016, 2016]

# MAKE THE PLOT
fig, axes = plt.subplots(nrows=2, ncols=4, subplot_kw={'projection': map_proj}, figsize=(16, 5))
for i,(month,year) in enumerate(zip(months_plot, years_plot)):
    def selector(ds):
        ds = ds.sel(time = ds['time.month']==month)
        ds = ds.sel(time = ds['time.year'] == year)
        return(ds.mean(dim='time'))

    ax = axes[0, i] # STREAMFUNCTION
    C0 = selector(psi850).plot.contourf(
        ax=ax, transform = data_proj, cmap = 'PuOr', extend="both",
        levels = np.linspace(-5e4, 5e4, 11),
        add_colorbar=False
    )
    ax.set_title('{} {}'.format(calendar.month_name[month], year))

    ax = axes[1, i]
    C1 = selector(prcp).plot.contourf(
        ax=ax, transform = data_proj, cmap = 'PuOr', extend="both",
        levels = np.linspace(-9, 9, 10),
        add_colorbar=False
    )
    ax.set_title('')

viz.FormatAxes(axes[0,:], extent = region.southern_hemisphere.as_extent())
viz.FormatAxes(axes[1,:], extent = region.south_america.as_extent())
fig.tight_layout()

fig.subplots_adjust(right=0.935)
cax0 = fig.add_axes([0.97, 0.55, 0.01, 0.4])
cax1 = fig.add_axes([0.97, 0.05, 0.01, 0.4])
cbar0 = fig.colorbar(C0, cax = cax0)
cbar0.formatter.set_powerlimits((7, 7))
cbar0.update_ticks()
cbar0.set_label(r'$\psi_{850}$ Anomaly [$m^2$/s]', rotation=270)
cbar0.ax.get_yaxis().labelpad = 20
cbar1 = fig.colorbar(C1, cax=cax1)
cbar1.set_label('Precip. Anomaly [mm/d]', rotation=270)
cbar1.ax.get_yaxis().labelpad = 20

fig.savefig(os.path.join(paths.figures, 'circulation-NDJF-1516-anomaly.pdf'), bbox_inches='tight')
