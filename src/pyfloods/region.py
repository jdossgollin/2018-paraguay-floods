# Define spatial and temporal boundaries of the analysis
import datetime

class Region:
    def __init__(self, lon, lat):
        from numpy import min
        from numpy import max
        self.lonmin = min(lon)
        self.lonmax = max(lon)
        self.latmin = min(lat)
        self.latmax = max(lat)

    def as_extent(self):
        extent = [self.lonmin, self.lonmax, self.latmin, self.latmax]
        return(extent)

    def as_patch(self, label='', color='blue', fill=None, linewidth=2):
        from matplotlib import patches
        dx = self.lonmax - self.lonmin
        dy = self.latmax - self.latmin
        rec = patches.Rectangle(
            (self.lonmin, self.latmin), dx, dy,
            color = color,
            label = label,
            fill = fill,
            linewidth=linewidth,
            transform = ccrs.PlateCarree()
        )
        return(rec)

wtype = Region(lon = [-65, -45], lat = [-30, -15])
lower_py_river = Region(lon = [-59.75, -55.75], lat = [-27.75, -22.75])
south_america = Region(lon = [-85, -30], lat = [-40, 5])
southern_hemisphere = Region(lon = [-120, 0], lat = [-50, 5])
reanalysis = Region(lon = [-180, 180], lat = [-60, 10])
rainfall = Region(lon = [-90, -30], lat = [-60, 10])

syear = 1979
eyear = 1981
sdate = datetime.date(syear, 1, 1)
edate = datetime.date(syear, 12, 31)
