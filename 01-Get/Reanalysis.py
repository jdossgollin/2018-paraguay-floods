'''
Read in reanalysis data from NCEP-NCAR Reanalysis I data set.

The approach to data management here is to try to minimize the number of times data needs to be re-downloaded (trial and error is a tough teacher...).
Consequently, we first download a relatively complete data set (all years in our range, and all levels in our range).
That is implemented in this notebook.
Later, we calculate anomalies and climatologies for a subset of the data -- this is very quick and if we change our spatial or temporal domain, we don't need to re-download anything.

Now, for each level, we will run through each year from `syear` to `eyear`.
Then, for each year, we will:

 1. Download the six-hour zonal ($u$) wind for that level and year and save to file
 2. Download the six-hour meridional ($v$) wind for that level ande year and save to file
 3. Calculate the six-hour streamfunction ($\psi$) for that year and save to file

The `overwrite` parameter specified above determines whether the data is downloaded even if the file is already on disk -- this can be useful for downloading a bit at a time.
'''

import numpy as np
import xarray as xr
import os
from paraguayfloodspy.pars  import GetPars
from windspharm.xarray import VectorWind

def main():
    # Define the Parameters
    time_pars = GetPars('time')
    syear,eyear = time_pars['syear'], time_pars['eyear']
    levels = [850]
    years = np.arange(syear, eyear+1)
    overwrite = False # overwrite existing data?

    # Loop through and download each required file
    for level_i in levels:
        print("Now working on {}hPa data".format(level_i))
        for year_i in years:
            # Define URL and Output File Names
            url_u = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/pressure/uwnd.{}.nc'.format(year_i)
            url_v = 'https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/pressure/vwnd.{}.nc'.format(year_i)
            fname_u = '_data/reanalysis/raw/uwnd_{}_{}.nc'.format(level_i, year_i)
            fname_v = '_data/reanalysis/raw/vwnd_{}_{}.nc'.format(level_i, year_i)
            fname_streamfunc = '_data/reanalysis/raw/streamfunc_{}_{}.nc'.format(level_i, year_i)
            if (os.path.isfile(fname_u) and os.path.isfile(fname_v) and os.path.isfile(fname_streamfunc)) and not overwrite:
                print("\tData for {} already exists -- not re-downloading".format(year_i))
            else:
                print("\tDownloading data for {}".format(year_i))
                # Get the raw wind
                U = xr.open_dataarray(url_u).sel(level=level_i).load()
                V = xr.open_dataarray(url_v).sel(level=level_i).load()
                # Get streamfunction
                W = VectorWind(U, V)
                streamfunc = W.streamfunction()
                # Save to file
                streamfunc.to_netcdf(fname_streamfunc, format='NETCDF4')

if __name__ == '__main__':
    main()
