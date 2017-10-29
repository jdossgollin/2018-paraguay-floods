'''
Get the weather types using the implementation in paraguayfloodspy
'''

import xarray as xr
import pandas as pd
import numpy as np
from paraguayfloodspy.weather_type import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--psi850', nargs=1, help='The 850 hPa streamfunction to read in')
parser.add_argument('--latlim', type=float, nargs=2, help = 'LATMIN, LATMAX')
parser.add_argument('--lonlim', type=float, nargs=2, help = 'LONMIN, LATMAX')
parser.add_argument('--ncluster', type=int, nargs=1, help = 'how many clusters to have')
parser.add_argument('--pcscaling', type=int, nargs=1, help = '0 or 1')
parser.add_argument('--wtprop', type=float, nargs=1, help = 'what fraction of variance to retain')
parser.add_argument('--nsim', type=int, nargs=1, help = 'how many simulatinos to run')
parser.add_argument('--outfile', nargs=1, help='The output file to save')

def main():
    args = parser.parse_args()
    latmin, latmax = np.min(args.latlim), np.max(args.latlim)
    lonmin, lonmax = np.min(args.lonlim), np.max(args.lonlim)
    outfile = args.outfile[0]
    n_clusters = args.ncluster[0]
    wt_prop = args.wtprop[0]
    nsim = args.nsim[0]
    pcscaling = args.pcscaling[0]

    psi = xr.open_dataset(args.psi850[0])
    psi = psi.sel(lon = slice(lonmin, lonmax), lat = slice(latmax, latmin))

    # TO REPRODUCE OUR RESULTS
    np.random.seed(22590)

    # All the computation is in the paraguayfloodspy.weather_type module
    best_centroid, best_ts, classifiability = XrEofCluster(
        psi,
        n_clusters=n_clusters,
        prop=wt_prop, # What proportion of variance should be retained?
        nsim=nsim, # How many random initializations to compute?
        pcscaling=pcscaling,
        variable='anomaly',
        verbose = True # get useful info from the algorithm
    )
    print("Classifiability Index: {}".format(classifiability))

    df = pd.DataFrame({'wtype': pd.Series(np.int_(best_ts), index=psi.time)})
    df.to_csv(outfile)

if __name__ == '__main__':
    main()
