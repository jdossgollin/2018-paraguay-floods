"""
This implements a single variable and single level of a reanalysis
V2 variable
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""
import xarray as xr
import numpy as np
import datetime
from typing import Dict,Tuple,List

from pyfloods.dataset import SingleFileDataSet

class CPCYear(SingleFileDataSet):
    """This implements just a single year!
    """

    def __init__(self, fname:str, verbose: bool = False, params: Dict ={}) -> None:
        self.year = params.get('year')
        super().__init__(fname=fname, params=params, verbose=verbose)

    def download_data(self) -> xr.DataArray:
        def convert_t_to_time(Tvec) -> np.ndarray:
            times = np.array([datetime.date(1960, 1, 1) + datetime.timedelta(np.int(ti)) for ti in Tvec])
            return(np.array(times))

        def convert_time_to_t(date)  -> np.ndarray:
            date_diff = date - datetime.date(1960,1,1)
            T = date_diff.days
            return(T)

        if self.year >= 1979 and self.year <= 2005:
            url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.RETRO/.rain/dods'
        elif self.year >= 2006 and self.year <= 2016:
            url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.REALTIME/.rain/dods'
        else:
            raise ValueError('You have entered an invalid year. {} is outside range [1979, 2016]'.format(self.year))

        Tstart = convert_time_to_t(datetime.date(self.year, 1, 1))
        Tend = convert_time_to_t(datetime.date(self.year, 12, 31))

        ds = xr.open_dataarray(url, decode_times=False)
        ds = ds.sel(T = slice(Tstart, Tend)).load()
        ds = ds.rename({'X': 'lon', 'Y': 'lat', 'T': 'time'})
        ds['time'] = convert_t_to_time(ds['time'])
        ds['time'] = ds['time'].astype('datetime64')
        lon_new = ds['lon'].values.copy()
        lon_new[np.where(lon_new > 180.0)] -= 360
        ds['lon'].values = lon_new
        ds = ds.sortby('lon')
        ds = ds.sortby('lat')
        ds.attrs['year'] = self.year
        ds.to_netcdf(self.fname, format='NETCDF4', mode='w')

        return ds

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataarray(self.fname)
        pars = {
            'year': ds.attrs.get('year')
        }
        return ds, pars

class CPC():
    """This implements multiple years!
    """
    def __init__(self, fnames: List[str], years: List[int], verbose: bool =False, params: Dict ={}) -> None:
        assert len(fnames) == len(years), 'You must have same number of filenames ane years'

        self.assets: List[CPCYear] = []
        for y,fn in zip(years, fnames):
            par_full = params.copy()
            par_full.update({'year': y})
            self.assets.append(CPCYear(fname=fn, verbose=verbose, params=par_full))
        self.fnames = [asset.fname for asset in self.assets]

    def get_data(self) -> None:
        for asset in self.assets:
            asset.get_data()
        return xr.open_mfdataset(self.fnames)
