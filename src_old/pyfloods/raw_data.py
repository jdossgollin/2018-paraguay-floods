"""
Here we will define some datasets that use the dataset package
but are specifically defined for this project.
"""

import xarray as xr
import numpy as np
from datetime import datetime
import os

from pyfloods.dataset import MJOBOMD, KaplanNINO34, NOAANGDC, S2SAreaAvg, ReanalysisV2, CPC, CMBGLOBAL
from pyfloods import paths
from pyfloods import region

verbose = False # universal

mjo = MJOBOMD(
    fname = os.path.abspath(os.path.join(paths.data_external, 'mjo.csv')),
    params = {'sdate': region.sdate, 'edate': region.edate},
    verbose = verbose
)
enso = KaplanNINO34(
    fname = os.path.abspath(os.path.join(paths.data_external, 'nino_34.csv')),
    params = {'sdate': region.sdate, 'edate': region.edate},
    verbose = verbose
)
topo = NOAANGDC(
    fname = os.path.abspath(os.path.join(paths.data_external, 'elevation_data.nc')),
    verbose = verbose
)
sst = CMBGLOBAL(
    fname = os.path.abspath(os.path.join(paths.data_external, 'cmb_sst_data.nc')),
    verbose = verbose
)
s2s = S2SAreaAvg(
    fname = os.path.abspath(os.path.join(paths.data_external, 's2s_area_avg.nc')),
    verbose = verbose
)
years = np.arange(region.syear, region.eyear+1)
u850 = ReanalysisV2(
    fnames = [os.path.join(paths.data_external, 'reanalysisv2_uwnd_850_{}.nc'.format(y)) for y in years],
    years = years,
    verbose = verbose,
    params={'coord_system': 'pressure', 'level': 850, 'var': 'uwnd'}
)
v850 = ReanalysisV2(
    fnames = [os.path.join(paths.data_external, 'reanalysisv2_vwnd_850_{}.nc'.format(y)) for y in years],
    years = years,
    verbose = verbose,
    params={'coord_system': 'pressure', 'level': 850, 'var': 'vwnd'}
)
cpc = CPC(
    [os.path.join(paths.data_external, 'cpc_rain_{}.nc'.format(y)) for y in years],
    years = years,
    verbose = verbose, params={}
)
