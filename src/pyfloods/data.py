import xarray as xr
import numpy as np
import os

class R2Var():
    def __init__(self, coord_system, var, syear, eyear, level, verbose=False, overwrite=False):
        from .paths import data_external

        self.coord_system = coord_system
        self.var = var
        self.level = level
        self.years = np.arange(syear, eyear+1)
        self.urls = ['https://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2/{}/{}.{}.nc'.format(self.coord_system, self.var, year) for year in self.years]
        self.fnames = [os.path.join(data_external, '{}_{}_{}.nc'.format(self.var, self.level, year)) for year in self.years]
        self._download(verbose=verbose, overwrite=overwrite)

    def _download(self, verbose=False, overwrite=False):
        import xarray as xr
        import numpy as np
        import os
        from .paths import data_external

        for url,fname in zip(self.urls, self.fnames):
            if os.path.exists(fname) and not overwrite:
                if verbose: print('File {} already exists'.format(fname))
            else:
                if verbose:
                    print('Loading data from url {} and saving to {}'.format(url,fname))
                ds = xr.open_dataarray(url, decode_cf = False).sel(level = self.level)
                del ds.attrs['_FillValue']
                scale = ds.attrs['scale_factor']
                offset = ds.attrs['add_offset']
                ds.values = ds.values * scale + offset
                lon_new = ds['lon'].values.copy()
                lon_new[np.where(lon_new > 180.0)] -= 360
                ds['lon'].values = lon_new
                ds = ds.sortby('lon')
                ds.to_netcdf(fname, format='NETCDF4')

class CPCVar():
    def __init__(self, syear, eyear, verbose=False, overwrite=False):
        from .paths import data_external

        self.years = np.arange(syear, eyear+1)
        self._calcurl()
        self.fnames = [os.path.join(data_external, 'cpc_rainfall_{}.nc'.format(year)) for year in self.years]
        self._download(verbose=verbose, overwrite=overwrite)

    def _calcurl(self):
        def url_fun(year):
            if year >= 1979 and year <= 2005:
                url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.RETRO/.rain/dods'
            elif year >= 2006 and year <= 2016:
                url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.UNIFIED_PRCP/.GAUGE_BASED/.GLOBAL/.v1p0/.REALTIME/.rain/dods'
            else:
                raise ValueError('You have entered an invalid year. {} is outside range [1979, 2016]'.format(year))
            return(url)
        self.urls = [url_fun(y) for y in self.years]

    def _download(self, verbose=False, overwrite=False):
        import datetime
        from .paths import data_external

        def convert_t_to_time(Tvec):
            times = np.array([datetime.date(1960, 1, 1) + datetime.timedelta(np.int(ti)) for ti in Tvec])
            return(np.array(times))
        def convert_time_to_t(date):
            date_diff = date - datetime.date(1960,1,1)
            T = date_diff.days
            return(T)

        for year,url,fn in zip(self.years, self.urls, self.fnames):
            if os.path.exists(fn) and not overwrite:
                if verbose: print('File {} already exists'.format(fn))
            else:
                if verbose:
                    print('Loading data from url {} and saving to {}'.format(url,fn))
                Tstart = convert_time_to_t(datetime.date(year, 1, 1))
                Tend = convert_time_to_t(datetime.date(year, 12, 31))
                ds = xr.open_dataarray(url, decode_times=False)
                ds = ds.sel(T = slice(Tstart, Tend))
                ds.load() # force it to download
                ds = ds.rename({'X': 'lon', 'Y': 'lat', 'T': 'time'})
                ds['time'] = convert_t_to_time(ds['time'])
                ds['time'] = ds['time'].astype('datetime64')
                lon_new = ds['lon'].values.copy()
                lon_new[np.where(lon_new > 180.0)] -= 360
                ds['lon'].values = lon_new
                ds = ds.sortby('lon')
                ds.to_netcdf(fn, format='NETCDF4')

class UV2Psi():
    def __init__(self, U, V, overwrite = False, verbose = False):

        from windspharm.xarray import VectorWind
        from .paths import data_processed

        assert np.all(U.years == V.years), 'Data do not match years'
        assert np.all(U.level == V.level), 'Data do not match levels'

        self.years = U.years
        self.level = U.level
        self.fnames = [os.path.join(data_processed, 'psi_{}_{}.nc'.format(self.level, year)) for year in self.years]

        for uw,vw,fn in zip(U.fnames, V.fnames, self.fnames):
            if os.path.exists(fn) and not overwrite:
                if verbose: print('File {} already exists'.format(fn))
            else:
                U = xr.open_dataarray(uw)
                V = xr.open_dataarray(vw)
                W = VectorWind(U, V)
                streamfunc = W.streamfunction()
                streamfunc.to_netcdf(fn, format='NETCDF4')

def make_anomalies(fnames, varname, region, outfile, overwrite=False, verbose=False):
    if os.path.exists(outfile) and not overwrite:
        if verbose:
            print('File {} already exists'.format(outfile))
        ds = xr.open_dataset(outfile)
    else:
        if verbose:
            print('Creating anomaly and raw data and saving to file {}'.format(outfile))

        raw = xr.open_mfdataset(fnames)[varname].sortby('lat').sel(
            lon = slice(region.lonmin, region.lonmax),
            lat = slice(region.latmin, region.latmax)
        )
        year = raw['time.year']
        month = raw['time.month']
        year_adj = year
        year_adj[np.in1d(month, [11, 12])] += 1
        raw.coords['year_adj'] = year_adj
        syear = np.min(year_adj.values)
        eyear = np.max(year_adj.values)
        raw = raw.sel(time = slice('{}-11-01'.format(syear), '{}-02-28'.format(eyear)))
        raw = raw.sel(time = np.in1d(raw['time.month'], [11, 12, 1, 2]))
        anomaly = raw - raw.mean(dim='time')
        ds = xr.Dataset({'raw': raw, 'anomaly': anomaly})
        ds.to_netcdf(outfile, format='NETCDF4')
    return(ds)

def get_monthly_indices(overwrite=False, verbose=False, raw_url=None, col_name=None):
    import pandas as pd
    from .region import sdate, edate
    from .paths import monthly_indices
    def read_indices(raw_url=None, col_name=None):
        df = pd.read_table(raw_url, delim_whitespace=True,index_col=None, skiprows=2, names=['time', '{}'.format(col_name)])
        df['time'] = np.int_(np.floor(df['time']))
        df['year'] = 1960 + df['time'] // 12
        df['month'] = 1 + df['time'] % 12
        df['day'] = 1
        df['time'] = pd.to_datetime(df[['year', 'month', 'day']])
        df.index = df['time']
        df = df[['{}'.format(col_name)]]
        return(df)
    if os.path.exists(monthly_indices) and not overwrite:
        if verbose:
            print('File {} already exists'.format(monthly_indices))
        df = pd.read_csv(monthly_indices, parse_dates=True, index_col='time')
    else:
        if verbose:
            print('Getting monthly indices and saving to file {}'.format(monthly_indices))
        df = read_indices(
            raw_url = 'http://iridl.ldeo.columbia.edu/SOURCES/.Indices/.nino/.EXTENDED/.NINO34/gridtable.tsv',
            col_name = 'nino_34'
        )
        df = df[sdate:edate]
        df.to_csv(monthly_indices)
    return(df)

def get_daily_indices(overwrite=False, verbose=False):
    import pandas as pd
    from .region import sdate, edate
    from .paths import daily_indices

    if os.path.exists(daily_indices) and not overwrite:
        if verbose:
            print('File {} already exists'.format(daily_indices))
        df = pd.read_csv(daily_indices, parse_dates=True, index_col='time')
    else:
        if verbose:
            print('Getting monthly indices and saving to file {}'.format(daily_indices))
        raw_url = 'http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt'
        col_names = ['year', 'month', 'day', 'RMM1', 'RMM2', 'phase', 'amplitude', 'source']
        df = pd.read_table(raw_url, delim_whitespace=True,index_col=None, skiprows=2, names=col_names)
        df['time'] = pd.to_datetime(df[['year', 'month', 'day']])
        df.index = df['time']
        df = df[['RMM1', 'RMM2', 'phase', 'amplitude']]
        df = df[sdate:edate]
        df.to_csv(daily_indices)

    return(df)

def get_elevation(overwrite=False, verbose=False):
    from .paths import elevation_data

    if os.path.exists(elevation_data) and not overwrite:
        if verbose:
            print('File {} already exists'.format(elevation_data))
        elev = xr.open_dataarray(elevation_data)
    else:
        if verbose:
            print('Getting elevation data and saving to file {}'.format(elevation_data))
        url = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NGDC/.GLOBE/.topo/'
        url += 'X/-180/0.1/180/GRID/Y/-90/0.1/90/GRID/'
        url += 'dods'
        elev = xr.open_dataarray(url)
        elev.to_netcdf(elevation_data, format='NETCDF4')
    return(elev)

def GetS2SAreaAverage(overwrite=False, verbose=False):
    from .region import lower_py_river
    from .paths import s2s_area_avg

    if os.path.exists(s2s_area_avg) and not overwrite:
        if verbose:
            print('File {} already exists'.format(s2s_area_avg))
        ds = xr.open_dataarray(s2s_area_avg)
    else:
        if verbose:
            print('Getting S2S rainfall data and saving to file {}'.format(s2s_area_avg))

        extent = lower_py_river.as_extent()
        x0,x1 = extent[0], extent[1]
        y0,y1 = extent[2], extent[3]

        url = 'http://iridl.ldeo.columbia.edu/home/.mbell/.ECMWF/.S2Stest/.S2S/.ECMF_ph2/.forecast/.perturbed/.sfc_precip/.tp/'
        url += 'X/{}/{}/RANGEEDGES/'.format(x0, x1)
        url += 'Y/{}/{}/RANGEEDGES/'.format(y0, y1)
        url += '[X+Y]average/'
        url += 'L+differences/'
        url += 'dods'

        ds = xr.open_dataarray(url)
        ds = ds.sel(S = slice('2015-09-01', '2016-02-29'))
        ds['L'] = ds['L']

        ds.to_netcdf(s2s_area_avg, format="NETCDF4")
    return(ds)
