"""This module defines a Region.

Different documents can then define regions which can in turn be used
in various scripts and analyses
"""
import cartopy.crs as ccrs
import numpy as np
from matplotlib import patches

class Region:
    """Define a square region
    """
    def __init__(self, lon, lat):
        self.lonmin = np.min(lon)
        self.lonmax = np.max(lon)
        self.latmin = np.min(lat)
        self.latmax = np.max(lat)

    def as_extent(self):
        """Convert a Region to an extent to be used in set_extent methods
        """
        extent = [self.lonmin, self.lonmax, self.latmin, self.latmax]
        return extent

    def as_patch(self, **kwargs):
        """Convert a Region to a matplotlib patch
        """
        label = kwargs.pop('label', '')
        color = kwargs.pop('color', 'blue')
        fill = kwargs.pop('fill', None)
        linewidth = kwargs.pop('linewidth', 2)
        transform = kwargs.pop('transform', ccrs.PlateCarree())

        delta_x = self.lonmax - self.lonmin
        delta_y = self.latmax - self.latmin
        rec = patches.Rectangle(
            (self.lonmin, self.latmin), delta_x, delta_y,
            color=color,
            label=label,
            fill=fill,
            linewidth=linewidth,
            transform=transform
        )
        return rec
