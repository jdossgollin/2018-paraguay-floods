import xarray as xr
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from pyfloods import weather_type
from pyfloods import paths
from pyfloods.region import wtype as wtrgn
from pyfloods.anomalies import streamfunction

classifiability_file = os.path.join(paths.data_processed, 'classifiability.csv')
recalculate = False

try:
    cluster_ts = pd.read_csv(classifiability_file)
except:
    recalculate = True

if recalculate:
    psi = streamfunction.get_data()
    psi = psi.sel(lon = slice(wtrgn.lonmin, wtrgn.lonmax),
                  lat = slice(wtrgn.latmin, wtrgn.latmax))
    psi = psi.sel(time = np.in1d(psi['time.month'], [11, 12, 1, 2]))
    psi = psi.sel(time = slice('1979-11-01', '2016-02-29'))
    n_clusters = np.arange(2,10)
    class_idx = []
    for i,nc in enumerate(n_clusters):
        pars = {
            'n_clusters': nc,
            'wt_prop': 0.95,
            'nsim': 100,
            'pcscaling': 1
        }
        best_centroid, cluster_ts, classifiability = weather_type.XrEofCluster(
            ds=psi['anomaly'],
            n_clusters=pars.get('n_clusters'),
            prop=pars.get('wt_prop'),
            nsim=pars.get('nsim'),
            pcscaling=pars.get('pcscaling'),
            verbose = False
        )
        class_idx.append(classifiability)
    cluster_ts = pd.DataFrame({'n_clusters': n_clusters, 'classifiability': class_idx})
    cluster_ts.to_csv(classifiability_file)

# Plot
plt.figure(figsize=(7, 4))
plt.plot(cluster_ts['n_clusters'], cluster_ts['classifiability'])
plt.xlabel("Number of Weather Types")
plt.ylabel("Classifiability Index")
plt.grid()
plt.savefig(os.path.join(paths.figures, 'wt-classifiability.pdf'), bbox_inches='tight')
