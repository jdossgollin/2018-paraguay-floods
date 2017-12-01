import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from eofs.xarray import Eof
import os

from pyfloods.anomalies import streamfunction
from pyfloods.region import wtype
import pyfloods.paths
import pyfloods.visualize as viz

psi = streamfunction.get_data().sel(
    lon = slice(wtype.lonmin, wtype.lonmax),
    lat = slice(wtype.latmin, wtype.latmax))['anomaly']

solver = Eof(psi, center=True)
var_frac = solver.varianceFraction()
cumvar = np.cumsum(var_frac.values)

n_eof = np.arange(cumvar.size) + 1

# PLOT VARIANCE EXPLAINED
fig,axes = plt.subplots(nrows=1, ncols=2, sharey=False, figsize=(12, 4))

ax = axes[0]
ax.plot(n_eof, var_frac)
ax.scatter(n_eof, var_frac)
ax.set_ylabel('Variance Explained')
ax.grid()

ax = axes[1]
plt.plot(n_eof, cumvar)
plt.scatter(n_eof, cumvar)
ax.set_ylabel('Cumulative Variance')
ax.grid()
for ax in axes.flat:
    ax.set_xlim([0.8, 9.2])

fig.tight_layout()
fig.savefig(os.path.join(pyfloods.paths.figures, 'ssta-composite-wt4.pdf.pdf'), bbox_inches='tight')


# plot the EOF loadings
loading = solver.eofs(neofs=4)
loading['mode'] += 1

aspect = (loading.lon.max() - loading.lon.min()) / (loading.lat.max() - loading.lat.min())
p = loading.plot.contourf(
    transform=ccrs.PlateCarree(), col='mode', #figsize=(16, 3.5),
    aspect=aspect,
    subplot_kws={'projection': ccrs.PlateCarree()},
    cmap = "PuOr", levels=np.linspace(-0.3, 0.3, 13))
viz.FormatAxes(p.axes, coast=True, grid=False, border=True,
               ticks=[np.linspace(-180, 180, 91), np.linspace(-90, 90, 37)],
               extent=pyfloods.region.wtype.as_extent())
for i,ax in enumerate(p.axes.flat):
    ax.set_title('EOF {}'.format(i+1))
plt.savefig(os.path.join(pyfloods.paths.figures, 'eof-loadings.pdf'), bbox_inches='tight')
