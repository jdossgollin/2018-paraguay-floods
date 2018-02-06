"""
A SingleFileDataSet object for the sst data
http://iridl.ldeo.columbia.edu/expert/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/.Reyn_SmithOIv2/.monthly/.ssta/dods
"""
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict,Tuple

from pyfloods.dataset import SingleFileDataSet

class CMBGLOBAL(SingleFileDataSet):
    def __init__(self, fname:str, verbose: bool = False, params: Dict = {}) -> None:
        """The params must be a dict of datetime.datetime objects
        with names 'sdate' and 'edate'.
        """
        super().__init__(fname=fname, params=params, verbose=verbose)

    def download_data(self) -> xr.DataArray:
        url = 'http://iridl.ldeo.columbia.edu/expert/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/.Reyn_SmithOIv2/.monthly/.ssta/dods'
        ds = xr.open_dataarray(url, decode_times=False)
        time =np.int_(np.floor(ds['T']))
        year = 1960 + time // 12
        month = 1 + time % 12
        day = np.ones_like(month)
        time = pd.to_datetime(year * 10000 + month * 100 + 1, format="%Y%m%d")
        ds['T'] = time
        ds.to_netcdf(self.fname, format='NETCDF4', mode='w')
        return ds

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataarray(self.fname)
        pars: Dict[str, datetime] = {}
        return ds, pars
