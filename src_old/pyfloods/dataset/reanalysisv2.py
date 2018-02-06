"""
This implements a single variable and single level of a reanalysis
V2 variable
https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2
"""
import xarray as xr
import numpy as np
from typing import Dict,Tuple,List

from pyfloods.dataset import SingleFileDataSet

class RV2Year(SingleFileDataSet):
    """This implements just a single year!
    """

    def __init__(self, fname:str, verbose: bool = False, params: Dict ={}) -> None:
        self.coord_system = params.get('coord_system')
        self.var = params.get('var')
        self.level = params.get('level')
        self.year = params.get('year')
        super().__init__(fname=fname, params=params, verbose=verbose)

    def download_data(self) -> xr.DataArray:
        base_url = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2'
        self.url = '{}/{}/{}.{}.nc'.format(base_url, self.coord_system, self.var, self.year)
        ds = xr.open_dataarray(self.url, decode_cf = False).sel(level = self.level)
        ds.attrs.pop('_FillValue')
        scale = ds.attrs['scale_factor']
        offset = ds.attrs['add_offset']
        ds.values = ds.values * scale + offset
        lon_new = ds['lon'].values.copy()
        lon_new[np.where(lon_new > 180.0)] -= 360
        ds['lon'].values = lon_new
        ds = ds.sortby('lon')
        ds = ds.sortby('lat')
        ds.attrs['coord_system'] = self.coord_system
        ds.attrs['var'] = self.var
        ds.attrs['level'] = self.level
        ds.attrs['year'] = self.year
        ds.to_netcdf(self.fname, format='NETCDF4', mode='w')
        return ds

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataarray(self.fname)
        pars = {
            'coord_system': ds.attrs.get('coord_system'),
            'var': ds.attrs.get('var'),
            'level': ds.attrs.get('level'),
            'year': ds.attrs.get('year')
        }
        return ds, pars

class ReanalysisV2():
    """This implements multiple years!
    """
    def __init__(self, fnames: List[str], years: List[int], verbose: bool =False, params: Dict ={}) -> None:
        assert len(fnames) == len(years), 'You must have same number of filenames ane years'

        self.assets: List[RV2Year] = []
        for y,fn in zip(years, fnames):
            par_full = params.copy()
            par_full.update({'year': y})
            self.assets.append(RV2Year(fname=fn, verbose=verbose, params=par_full))
        self.fnames = [asset.fname for asset in self.assets]

    def get_data(self) -> None:
        for asset in self.assets:
            asset.get_data()
        combined = xr.open_mfdataset(self.fnames)
        return combined
