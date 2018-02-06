"""
A SingleFileDataSet object for the ECMWF S2S data
Specifically it returns the area-averaged rainfall over some box
http://iridl.ldeo.columbia.edu/home/.mbell/.ECMWF/.S2Stest/.S2S/.ECMF_ph2/.forecast/.perturbed/.sfc_precip/.tp/
"""
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime,timedelta
from typing import Dict,Tuple

from pyfloods.dataset import SingleFileDataSet

class S2SAreaAvg(SingleFileDataSet):
    def __init__(self, fname:str, verbose: bool = False, params: Dict = {}) -> None:

        super().__init__(fname=fname, params=params, verbose=verbose)

        self.sdate: datetime = self.params.get('sdate', datetime(2015, 9, 1))
        self.edate: datetime = self.params.get('edate', datetime(2016, 2, 29))
        self.lonmin: float = self.params.get('lonmin', -65)
        self.lonmax: float = self.params.get('lonmax', -45)
        self.latmin: float = self.params.get('latmin', -30)
        self.latmax: float = self.params.get('latmax', -15)
        self.params: Dict = {
            'sdate': self.sdate, 'edate': self.edate,
            'lonmin': self.lonmin, 'lonmax': self.lonmax,
            'latmin': self.latmin, 'latmax': self.latmax
        }

    def download_data(self) -> xr.DataArray:
        url = 'http://iridl.ldeo.columbia.edu/home/.mbell/.ECMWF/.S2Stest/.S2S/.ECMF_ph2/.forecast/.perturbed/.sfc_precip/.tp/'
        url += 'X/{}/{}/RANGEEDGES/'.format(self.lonmin, self.lonmax)
        url += 'Y/{}/{}/RANGEEDGES/'.format(self.latmin, self.latmax)
        url += '[X+Y]average/'
        url += 'L+differences/'
        url += 'dods'
        ds = xr.open_dataarray(url)
        ds = ds.sel(S = slice(self.sdate, self.edate))
        ds['S'] = pd.to_datetime(ds['S'].values)
        ds['L'] = ds['L']
        ds.attrs['lonmin'] = self.lonmin
        ds.attrs['lonmax'] = self.lonmax
        ds.attrs['latmin'] = self.latmin
        ds.attrs['latmax'] = self.latmax
        ds.to_netcdf(self.fname, format='NETCDF4', mode='w')
        return(ds)

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataarray(self.fname)
        pars: Dict[str, float] = {
            'lonmin': ds.attrs.get('lonmin'),
            'lonmax': ds.attrs.get('lonmax'),
            'latmin': ds.attrs.get('latmin'),
            'latmax': ds.attrs.get('latmax'),
            'sdate': pd.to_datetime(ds['S'].min().values),
            'edate': pd.to_datetime(ds['S'].max().values)
        }
        # Model isn't run every day but this messes up the param comparison
        ok_diff = timedelta(4)
        if ok_diff >= np.abs(pars.get('sdate') - self.params.get('sdate')):
            pars['sdate'] = self.params.get('sdate')
        if ok_diff >= np.abs(pars.get('edate') - self.params.get('edate')):
            pars['edate'] = self.params.get('edate')
        return ds, pars
