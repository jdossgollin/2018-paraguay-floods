'''
Subsetting, Anomalies, and Climatologies

In a previous notebook (`Reanalysis`) we created a relatively large database of raw $U,V,\psi$.
This is helpful, but for our visualizations it's nice to sub-set the data in advance so that all we have to do is load the relevant bits.
We'll also pre-compute anomalies and climatologies, which saves substantial computational time down the road at the expense of a bit of file storage.
Because we don't need the fine time resolution, we'll also re-sample everything to a daily time step (note that we didn't just download daily reanalysis data because we need to shift the end-of-day time!)
'''

import xarray as xr
import glob
import os
from paraguayfloodspy.xrutil import *
from paraguayfloodspy.pars import *

def main():
    pars = GetPars('all')
    syear, eyear = pars['time']['syear'], pars['time']['eyear']
    overwrite = False

    # 1. REANALYSIS DATA
    def transfer_fn(var, lonmin, lonmax, latmin, latmax, shift_time_h, return_daily, months):
        var = var.sel(lon = slice(lonmin, lonmax), lat = slice(latmax, latmin))
        # shift time by hours, if desired
        if shift_time_h != 0:
            time_old = var.time.values
            time_new = time_old + np.timedelta64(12, 'h')
            var['time'] = time_new
        # resample to daily time step, if desired
        if return_daily:
            var = var.resample('1D', dim = 'time')
        # subset months if required
        if months is not None:
            var = var.sel(time = np.in1d(var['time.month'], months))
        return(var)

    trans_lam = lambda ds: transfer_fn(
        var=ds,
        lonmin=pars['clim_plot']['lonmin'],
        lonmax=pars['clim_plot']['lonmax'],
        latmin=pars['clim_plot']['latmin'],
        latmax=pars['clim_plot']['latmax'],
        months=pars['months'],
        shift_time_h=12, return_daily=True)

    for var in ['streamfunc']:
        for level_i in [850]:
            fnames = glob.glob('_data/reanalysis/raw/{}_{}_*.nc'.format(var, level_i))
            raw_fname = "_data/reanalysis/subset/{}_{}_raw.nc".format(var, level_i)
            anom_fname = "_data/reanalysis/subset/{}_{}_anom.nc".format(var, level_i)
            clim_fname = "_data/reanalysis/subset/{}_{}_clim.nc".format(var, level_i)
            if len(fnames) > 0:
                if (os.path.isfile(raw_fname) and os.path.isfile(anom_fname) and os.path.isfile(clim_fname) and not overwrite):
                    print("Data for {}-{} has already been compiled; will not overwrite".format(level_i, var))
                else:
                    ds = read_netcdfs(fnames, dim='time', transform_func=trans_lam)
                    climatology, anomaly = CalcAnomaly(ds, ret_clim=True)
                    ds.to_netcdf(raw_fname)
                    anomaly.to_netcdf(anom_fname)
                    climatology.to_netcdf(clim_fname)
            else:
                print("No {} data at {}hPa".format(var, level_i))

    # RAINFALL DATA
    def transfer_fn(var, lonmin, lonmax, latmin, latmax, months):
        var = var.sel(lon = slice(lonmin, lonmax), lat = slice(latmin, latmax))
        if months is not None:
            var = var.sel(time = np.in1d(var['time.month'], months))
        return(var)

    trans_lam = lambda ds: transfer_fn(
        var=ds,
        lonmin=pars['rain']['lonmin'],
        lonmax=pars['rain']['lonmax'],
        latmin=pars['rain']['latmin'],
        latmax=pars['rain']['latmax'],
        months=pars['months']
    )

    fnames = glob.glob('_data/rainfall/raw/*.nc')
    raw_fname = "_data/rainfall/subset/cpc_raw.nc"
    anom_fname = "_data/rainfall/subset/cpc_anom.nc"
    clim_fname = "_data/rainfall/subset/cpc_clim.nc"
    if len(fnames) > 0:
        if (os.path.isfile(raw_fname) and os.path.isfile(anom_fname) and os.path.isfile(clim_fname) and not overwrite):
            print("Rainfall data has already been compiled; will not overwrite")
        else:
            ds = read_netcdfs(fnames, dim='time', transform_func=trans_lam)
            climatology, anomaly = CalcAnomaly(ds, ret_clim=True)
            ds.to_netcdf(raw_fname)
            anomaly.to_netcdf(anom_fname)
            climatology.to_netcdf(clim_fname)
    else:
        print("No rainfall data")

if __name__ == '__main__':
    main()
