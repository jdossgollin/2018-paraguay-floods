import xarray as xr
import numpy as np
from typing import Dict,Tuple,List
from windspharm.xarray import VectorWind
import os

from pyfloods.dataset.reanalysisv2 import RV2Year
from pyfloods.dataset import SingleFileDataSet,ReanalysisV2
from pyfloods import paths
from pyfloods import raw_data
from pyfloods import region

class PsiYear(SingleFileDataSet):
    """Turn a single year of uwind and vwind into streamfunction
    """

    def __init__(self, fname: str, uwnd: RV2Year, vwnd: RV2Year, verbose:bool = False) -> None:
        params: Dict = uwnd.params.copy()
        params.update({'var': 'psi'})
        self.params = params
        self.coord_system = params.get('coord_system')
        self.var = params.get('var')
        self.level = params.get('level')
        self.year = params.get('year')
        self.fname = fname
        self.uwnd = uwnd
        self.vwnd = vwnd
        super().__init__(fname=self.fname, params=params, verbose=verbose)

    def download_data(self) -> xr.DataArray:
        U = self.uwnd.get_data()
        V = self.vwnd.get_data()
        W = VectorWind(U, V)
        streamfunc = W.streamfunction()
        streamfunc.to_netcdf(self.fname, format='NETCDF4')
        streamfunc.attrs['coord_system'] = self.params.get('coord_system')
        streamfunc.attrs['level'] = self.params.get('level')
        streamfunc.attrs['year'] = self.params.get('year')
        streamfunc.attrs['var'] = self.params.get('var')
        streamfunc.to_netcdf(self.fname, format='NETCDF4')
        return streamfunc

    def read_data(self) -> Tuple[xr.DataArray, Dict]:
        ds = xr.open_dataarray(self.fname)
        pars = {
            'coord_system': ds.attrs.get('coord_system'),
            'var': ds.attrs.get('var'),
            'level': ds.attrs.get('level'),
            'year': ds.attrs.get('year')
        }
        return ds, pars

class PsiMulti():
    def __init__(self, uwnd: ReanalysisV2, vwnd: ReanalysisV2, fnames: List[str], years: List[int], verbose: bool = False) -> None:
        self.assets: List[PsiYear] = []
        for u,v,fn in zip(uwnd.assets, vwnd.assets, fnames):
            self.assets.append(PsiYear(fname = fn, uwnd=u, vwnd=v, verbose=False))
        self.fnames = [asset.fname for asset in self.assets]

    def get_data(self) -> None:
        for asset in self.assets:
            asset.get_data()
        combined = xr.open_mfdataset(self.fnames)
        return combined

years = np.arange(region.syear, region.eyear + 1)
psi = PsiMulti(
    uwnd=raw_data.u850, vwnd=raw_data.v850,
    fnames = [os.path.join(paths.data_processed, 'reanalysisv2_psi_850_{}.nc'.format(y)) for y in years],
    years=years, verbose=False
)
