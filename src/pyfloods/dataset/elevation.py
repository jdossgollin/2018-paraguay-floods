"""
A SingleFileDataSet object for the NOAA NGDC GLOBE topographic dataset
stored on the iridl data library:
http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/
"""
import xarray as xr
from datetime import datetime
from typing import Dict,Tuple

from pyfloods.dataset import SingleFileDataSet

class NOAANGDC(SingleFileDataSet):
    def __init__(self, fname:str, verbose: bool = False, params: Dict = {}) -> None:
        """The params must be a dict of datetime.datetime objects
        with names 'sdate' and 'edate'.
        """
        super().__init__(fname=fname, params=params, verbose=verbose)

    def download_data(self) -> xr.DataArray:
        url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/'
        url += 'X/-180/0.1/180/GRID/Y/-90/0.1/90/GRID/'
        url += 'dods'
        ds = xr.open_dataarray(url)
        ds.to_netcdf(self.fname, format='NETCDF4', mode='w')
        return ds

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataarray(self.fname)
        pars: Dict[str, datetime] = {}
        return ds, pars
