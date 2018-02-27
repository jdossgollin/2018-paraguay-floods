#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Plot classifiability as a function of # weather types
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--infiles", help="The classifiability indices")

def main():
    """Run everything
    """
    args = parser.parse_args()
    
    fnames = glob(args.infiles)
    arrays = [xr.open_dataarray(fn) for fn in fnames]
    classifiability = np.array([ds.attrs['class_idx'] for ds in arrays])
    n_wtype = np.array([np.unique(ds.values).size for ds in arrays])

    df = pd.DataFrame({'classifiability': classifiability, 'n_wtype': n_wtype}).sort_values('n_wtype').set_index('n_wtype')

    # Plot
    df['classifiability'].plot(figsize=(15, 4.5), grid=True)
    plt.xlabel('Number of Weather Types')
    plt.ylabel('Classifiability Index')

    # Save the plot
    plt.savefig(args.outfile, bbox_inches='tight')

if __name__ == "__main__":
    main()
