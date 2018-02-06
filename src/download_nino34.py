#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download raw NINO 3.4  data from
http://iridl.ldeo.columbia.edu/SOURCES/.Indices/.nino/.EXTENDED/.NINO34
and parse it
"""

import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--syear", help="the first year to retain")
parser.add_argument("--eyear", help="the last year to retain")
parser.add_argument("--outfile", help="the filename of the data to save")

def download_data(sdate, edate, outfile):
    """Load in the NINO 3.4 Data
    """
    url = 'http://iridl.ldeo.columbia.edu/SOURCES/.Indices/.nino/.EXTENDED/.NINO34/gridtable.tsv'
    col_name = 'nino_34'
    nino_34 = pd.read_table(
        url, delim_whitespace=True, index_col=None, skiprows=2,
        names=['time', '{}'.format(col_name)]
    )

    # the times don't make sense, parse them in
    nino_34['time'] = np.int_(np.floor(nino_34['time']))
    nino_34['year'] = 1960 + nino_34['time'] // 12
    nino_34['month'] = 1 + nino_34['time'] % 12
    nino_34['day'] = 1
    nino_34['time'] = pd.to_datetime(nino_34[['year', 'month', 'day']])
    nino_34.set_index('time', inplace=True)
    nino_34 = nino_34[['{}'.format(col_name)]]
    nino_34 = nino_34.loc[sdate:edate]
    nino_34 = nino_34.to_xarray()

    # save to file
    if os.path.isfile(outfile):
        os.remove(outfile)
    nino_34.to_netcdf(outfile, format='NETCDF4', mode='w')

def main():
    """Parse the command line arguments and run download_data().
    """
    args = parser.parse_args()
    outfile = os.path.abspath(args.outfile)
    sdate = datetime(int(args.syear), 1, 1)
    edate = datetime(int(args.eyear), 12, 31)
    download_data(sdate=sdate, edate=edate, outfile=outfile)

if __name__ == "__main__":
    main()
