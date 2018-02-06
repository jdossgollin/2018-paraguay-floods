import xarray as xr
import numpy as np
import pandas as pd
import os
from typing import Dict,Any,List,Tuple
from datetime import datetime

from pyfloods.dataset import SingleFileDataSet,CPC
from pyfloods.region import Region

class Anomaly(SingleFileDataSet):
    def __init__(self, superset: Any, fname: str, varname:str, region: Region,
                sdate: datetime, edate: datetime, months: List[int]=[11, 12, 1, 2],
                verbose: bool=False) -> None:
        self.superset = superset
        params: Dict = superset.assets[0].params.copy()
        params.pop('year', None); params.pop('level', None)
        params.pop('coord_system', None); params.pop('var', None)
        params.update({
            'sdate': sdate, 'edate': edate,
            'lonmin': region.lonmin.astype('float'),
            'lonmax': region.lonmax.astype('float'),
            'latmin': region.latmin.astype('float'),
            'latmax': region.latmax.astype('float')
        })
        self.varname = varname
        self.months = months
        super().__init__(fname=fname, params=params, verbose=verbose)

    def download_data(self) -> xr.DataArray:
        raw = self.superset.get_data()[self.varname]
        raw = raw.sortby('lat').sortby('lon')
        raw = raw.sel(
            lon = slice(self.params['lonmin'], self.params['lonmax']),
            lat = slice(self.params['latmin'], self.params['latmax'])
        )
        year = raw['time.year']
        month = raw['time.month']
        year_adj = year
        year_adj[np.in1d(month, [11, 12])] += 1
        raw.coords['year_adj'] = year_adj
        raw = raw.sel(time = slice(self.params.get('sdate'), self.params.get('edate')))
        raw = raw.sel(time = np.in1d(raw['time.month'], self.months))
        anomaly = raw - raw.mean(dim='time')
        ds = xr.Dataset({'raw': raw, 'anomaly': anomaly})
        ds.to_netcdf(self.fname, format='NETCDF4')
        return ds

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataset(self.fname)
        pars = {
            'edate': pd.to_datetime(ds['time'].max().values),
            'lonmin': ds['lon'].min().values.tolist(),
            'lonmax': ds['lon'].max().values.tolist(),
            'latmax': ds['lat'].max().values.tolist(),
            'latmin': ds['lat'].min().values.tolist(),
            'sdate': pd.to_datetime(ds['time'].min().values)
        }
        return ds, pars

from pyfloods import region
from pyfloods.raw_data import cpc
from pyfloods.streamfunction import psi
from pyfloods import paths

rainfall = Anomaly(
    superset = cpc, varname = 'rain',
    fname = os.path.join(paths.data_processed, 'rainfall.nc'),
    region = region.rainfall,
    sdate = pd.to_datetime(cpc.get_data().time.min().values),
    edate = pd.to_datetime(cpc.get_data().time.max().values),
    months = [11, 12, 1, 2]
)

streamfunction = Anomaly(
    superset = psi, varname='streamfunction',
    fname = os.path.join(paths.data_processed, 'streamfunction.nc'),
    region = region.reanalysis,
    sdate = pd.to_datetime(psi.get_data().time.min().values),
    edate = pd.to_datetime(psi.get_data().time.max().values),
    months = [11, 12, 1, 2]
)
