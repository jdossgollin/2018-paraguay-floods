'''
Read in daily indices (here just MJO) and save to file
'''

import pandas as pd
from paraguayfloodspy.pars  import GetPars

def main():
    time_pars = GetPars('time')
    syear,eyear = time_pars['syear'], time_pars['eyear']
    outfile = "_data/indices/daily_indices.csv"

    raw_url = 'http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt'
    col_names = ['year', 'month', 'day', 'RMM1', 'RMM2', 'phase', 'amplitude', 'source']


    # Now read in the data
    df = pd.read_table(raw_url, delim_whitespace=True,index_col=None, skiprows=2, names=col_names)

    # Convert the year-month-day structure to a standard time object and select only relevant columns
    df['time'] = pd.to_datetime(df[['year', 'month', 'day']])
    df.index = df['time']
    df = df[['RMM1', 'RMM2', 'phase', 'amplitude']]
    df = df['{}'.format(syear):'{}'.format(eyear)]

    # Check
    df.head(10)

    # Save to file
    df.to_csv(outfile)

if __name__ == '__main__':
    main()
