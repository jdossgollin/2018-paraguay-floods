import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches as patches
import datetime
import os

from pyfloods import visualize as viz
from pyfloods.anomalies import rainfall,streamfunction
from pyfloods.region import lower_py_river as lpr
import pyfloods.region
from pyfloods import paths


map_proj = ccrs.Orthographic(-60, -10)
data_proj = ccrs.PlateCarree()
days_back = [-2, -1, 0, 1]

psi = streamfunction.get_data()
prcp = rainfall.get_data()

prcp_rpy = prcp['raw'].sel(lon = slice(lpr.lonmin, lpr.lonmax),
                    lat = slice(lpr.latmin, lpr.latmax)).mean(
            dim=['lon', 'lat']).to_pandas()
rainy_days = prcp_rpy.loc[prcp_rpy > np.nanpercentile(prcp_rpy, 90)].index
rainy_days = pd.to_datetime(rainy_days)

# MAKE THE FIGURE
fig, axes = plt.subplots(nrows=2, ncols=len(days_back), subplot_kw={'projection': map_proj}, figsize=(16, 4.75))
for i,d in enumerate(days_back):
    def selector(ds):
        ds = ds.isel(time = np.in1d(ds.time, rainy_days + datetime.timedelta(days_back[i])))
        ds = ds.mean(dim='time')
        return(ds)

    ax = axes[0, i] # Streamfunction
    ax.set_title("t={} d".format(d))
    C0 = selector(psi['anomaly']).plot.contourf(
        transform = ccrs.PlateCarree(), ax=ax,
        cmap = 'PuOr', extend="both",
        levels=np.linspace(-2.1e4, 2.1e4, 8),
        add_colorbar=False, add_labels=False
    )

    ax = axes[1, i] # Rainfall
    C1 = selector(prcp['anomaly']).plot.contourf(
        transform = ccrs.PlateCarree(), ax=ax,
        cmap = 'BrBG', extend="both",
        levels = np.linspace(-12, 12, 13),
        add_colorbar=False, add_labels=False
    )

viz.FormatAxes(axes[0,:], extent = pyfloods.region.southern_hemisphere.as_extent())
sam_extent = pyfloods.region.south_america.as_extent() # modify this slightly
sam_extent[3] -= 7.5
viz.FormatAxes(axes[1,:], extent = sam_extent)

fig.tight_layout()
fig.subplots_adjust(right=0.935)
cax0 = fig.add_axes([0.97, 0.55, 0.01, 0.4])
cax1 = fig.add_axes([0.97, 0.05, 0.01, 0.4])
cbar0 = fig.colorbar(C0, cax = cax0)
cbar0.formatter.set_powerlimits((4, 4))
cbar0.update_ticks()
cbar0.set_label(r'$\psi_{850}$ Anomaly [$m^2$/s]', rotation=270)
cbar0.ax.get_yaxis().labelpad = 20
cbar1 = fig.colorbar(C1, cax=cax1)
cbar1.set_label('Precip. Anomaly [mm/d]', rotation=270)
cbar1.ax.get_yaxis().labelpad = 20

fig.savefig(os.path.join(paths.figures, 'lagged-rainfall.pdf'), bbox_inches='tight')
