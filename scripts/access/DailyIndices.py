'''
Read in daily indices (here just MJO) and save to file
'''

import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--years', type=int, nargs=2, help = 'LONMIN, LATMAX')
parser.add_argument('--outfile', nargs=1, help='The output file to save')

def main():

    args = parser.parse_args()
    syear, eyear = np.min(args.years), np.max(args.years)
    outfile=args.outfile[0]

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
