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

################################################################################
# Plot the anomalies
################################################################################
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

################################################################################
# Plot the anomalies using a different setup
################################################################################
map_proj = ccrs.PlateCarree()
fig, axes = plt.subplots(nrows=2, ncols=2, subplot_kw={'projection': map_proj}, figsize=(8, 5.25), sharex=True, sharey=True)
for i,(month,year) in enumerate(zip(months_plot, years_plot)):
    def selector(ds):
        ds = ds.sel(time = ds['time.month']==month)
        ds = ds.sel(time = ds['time.year'] == year)
        return(ds.mean(dim='time'))

    ax = viz.GetRowCol(i, axes)
    ax.set_title('{} {}'.format(calendar.month_name[month], year))
    C1 = selector(prcp).plot.contourf(
        transform = ccrs.PlateCarree(), ax=ax,
        cmap = 'BrBG', extend="both",
        levels=np.linspace(-6, 6, 13),
        add_colorbar=False, add_labels=False
    )
    psi_sub = selector(psi850)
    X,Y = np.meshgrid(psi_sub.lon, psi_sub.lat)
    C0 = ax.contour(X,Y,psi_sub.values,
        transform = ccrs.PlateCarree(),
        levels=np.linspace(-10e4, 10e4, 21),
        colors='k'
    )

my_extent = [-100, -20, -45, 10]
viz.FormatAxes(axes, extent = my_extent,
    ticks=[np.linspace(-180, 180, 19), np.linspace(-90, 90, 19)])

plt.tight_layout()
fig.subplots_adjust(right=0.925)
cax = fig.add_axes([0.965, 0.1, 0.02, 0.75])
cbar = fig.colorbar(C1, cax = cax)
cbar.set_label('Rainfall Anomaly [mm/day]', rotation=270)
cbar.ax.get_yaxis().labelpad = 20

fig.savefig(os.path.join(paths.figures, 'circulation-NDJF-1516-anomaly-alt.pdf'), bbox_inches='tight')
