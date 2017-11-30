"""
A SingleFileDataSet object for the MJO indices from the Australian BOM from
http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict,Tuple

from pyfloods.dataset import SingleFileDataSet

class MJOBOMD(SingleFileDataSet):
    def __init__(self, fname:str, verbose: bool = False, params = Dict[str, datetime]) -> None:
        """The params must be a dict of datetime.datetime objects
        with names 'sdate' and 'edate'.
        """
        super().__init__(fname=fname, params=params, verbose=verbose)
        self.sdate = self.params.get('sdate')
        self.edate = self.params.get('edate')

    def download_data(self) -> pd.DataFrame:
        raw_url = 'http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt'
        col_names = ['year', 'month', 'day', 'RMM1', 'RMM2', 'phase', 'amplitude', 'source']
        df = pd.read_table(raw_url, delim_whitespace=True,index_col=None, skiprows=2, names=col_names)
        df['time'] = pd.to_datetime(df[['year', 'month', 'day']])
        df = df.set_index('time')
        df = df[['RMM1', 'RMM2', 'phase', 'amplitude']]
        df = df.iloc[np.where(np.logical_and(df.index >= self.sdate, df.index <= self.edate))]
        df.to_csv(self.fname)
        return(df)

    def read_data(self) -> Tuple[pd.DataFrame, Dict]:
        df = pd.read_csv(self.fname, index_col='time', parse_dates=True)
        sdate = pd.to_datetime(df.index.min())
        edate = pd.to_datetime(df.index.max())
        pars: Dict[str, datetime] = {'sdate': sdate, 'edate': edate}
        return df, pars
