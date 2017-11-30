"""
A SingleFileDataSet object for the Kaplan NINO3.4 indices stored on the iridl
data library:
http://iridl.ldeo.columbia.edu/SOURCES/.Indices/.nino/.EXTENDED/.NINO34/
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict,Tuple

from pyfloods.dataset import SingleFileDataSet

class KaplanNINO34(SingleFileDataSet):
    def __init__(self, fname:str, verbose: bool = False, params = Dict[str, datetime]) -> None:
        """The params must be a dict of datetime.datetime objects
        with names 'sdate' and 'edate'.
        """
        super().__init__(fname=fname, params=params, verbose=verbose)
        self.sdate = self.params.get('sdate')
        self.edate = self.params.get('edate')

    def download_data(self) -> pd.DataFrame:
        raw_url = 'http://iridl.ldeo.columbia.edu/SOURCES/.Indices/.nino/.EXTENDED/.NINO34/gridtable.tsv'
        col_name = 'nino_34'
        df = pd.read_table(raw_url, delim_whitespace=True,index_col=None, skiprows=2, names=['time', '{}'.format(col_name)])
        df['time'] = np.int_(np.floor(df['time']))
        df['year'] = 1960 + df['time'] // 12
        df['month'] = 1 + df['time'] % 12
        df['day'] = 1
        df['time'] = pd.to_datetime(df[['year', 'month', 'day']])
        df.index = df['time']
        df = df[['{}'.format(col_name)]]
        df = df.iloc[np.where(np.logical_and(df.index >= self.sdate, df.index <= self.edate))]
        df.to_csv(self.fname)
        return(df)

    def read_data(self) -> Tuple[pd.DataFrame, Dict]:
        df = pd.read_csv(self.fname, index_col='time', parse_dates=True)
        sdate = pd.to_datetime(df.index.min())
        edate = pd.to_datetime(df.index.max())
        pars: Dict[str, datetime] = {'sdate': sdate, 'edate': edate}
        return df, pars
