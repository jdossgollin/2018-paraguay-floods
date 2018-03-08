#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Get proportion of weather types each year and save a latex table
"""

import argparse
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--wt", help="The Weather Type sequence")

def get_year_adj(time):
    """Given a datetime index, return the "year_adj" variable.

    This is the year that the NDJF season ended, so the period
    Nov 1979 to Feb 1980 has a "year_adj" of 1980.
    """
    month = time.month.values
    year_adj = time.year.values
    year_adj[np.in1d(month, [11, 12])] += 1
    return year_adj

def main():
    """Get the proportion of weather types and save a latex table
    """
    args = parser.parse_args()
    w_type = xr.open_dataarray(args.wt).to_dataframe()
    w_type['year_adj'] = get_year_adj(w_type.index)

    # Get prop of weather types by year
    wt_prop = w_type.groupby(['year_adj', 'wtype']).size().to_xarray()
    wt_prop = wt_prop / wt_prop.sum(dim='wtype')
    wt_prop = wt_prop.to_pandas()

    # Get NDJF 2015-16 and NDJF Climatology
    wt_prop_1516 = wt_prop.loc[2016]
    wt_prop_clim = wt_prop.mean()
    wt_prop_tex = pd.DataFrame({'climatology': wt_prop_clim, 'NDJF 2015-16': wt_prop_1516})

    # Save to latex table
    wt_prop_tex.round(decimals=3).to_latex(args.outfile)

if __name__ == "__main__":
    main()
