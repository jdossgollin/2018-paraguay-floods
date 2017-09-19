'''
Read in monthly indices (ENSO and PDO) and save to file
'''

import pandas as pd
import datetime
import numpy as np
from paraguayfloodspy.pars  import GetPars

def read_indices(raw_url, col_name):
    df = pd.read_table(raw_url, delim_whitespace=True,index_col=None, skiprows=2, names=['time', '{}'.format(col_name)])
    df['time'] = np.int_(np.floor(df['time']))
    df['year'] = 1960 + df['time'] // 12
    df['month'] = 1 + df['time'] % 12
    df['day'] = 1
    df['time'] = pd.to_datetime(df[['year', 'month', 'day']])
    df.index = df['time']
    df = df[['{}'.format(col_name)]]
    return(df)

def main():
    time_pars = GetPars('time')
    syear,eyear = time_pars['syear'], time_pars['eyear']
    outfile = "_data/indices/monthly_indices.csv"

    df = read_indices(
        raw_url = 'http://iridl.ldeo.columbia.edu/SOURCES/.Indices/.nino/.EXTENDED/.NINO34/gridtable.tsv',
        col_name = 'nino_34'
    )
    df = df['{}'.format(syear):'{}'.format(eyear)]

    # Save to file
    df.to_csv(outfile)

if __name__ == '__main__':
    main()
