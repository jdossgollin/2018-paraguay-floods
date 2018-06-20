"""Some functions for formatting axes with matplotlib and cartopy
"""

import cartopy.feature
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import numpy as np

def _format_axis(plt_ax, **kwargs):
    """Function to format a single axis. Should not be called directly.
    """
    coast = kwargs.pop('coast', True)
    grid = kwargs.pop('grid', False)
    river = kwargs.pop('river', False)
    border = kwargs.pop('border', False)
    states = kwargs.pop('states', False)
    extent = kwargs.pop('extent', None)
    feature_list = kwargs.pop('feature_list', None)
    xticks = kwargs.pop('xticks', None)
    yticks = kwargs.pop('yticks', None)
    crs = kwargs.pop('crs', ccrs.PlateCarree())

    plt_ax.axes.get_xaxis().set_ticklabels([])
    plt_ax.axes.get_yaxis().set_ticklabels([])
    plt_ax.set_xlabel('')
    plt_ax.set_ylabel('')

    if coast:
        plt_ax.coastlines()
    if border:
        plt_ax.add_feature(cartopy.feature.BORDERS)
    if river:
        plt_ax.add_feature(cartopy.feature.RIVERS)
    if states:
        states = cartopy.feature.NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines',
            scale='50m', facecolor='none'
        )
        plt_ax.add_feature(states, edgecolor='gray')

    if xticks is not None:
        plt_ax.set_xticks(xticks, crs=crs)
        lon_formatter = LongitudeFormatter()
        plt_ax.xaxis.set_major_formatter(lon_formatter)

    if yticks is not None:
        plt_ax.set_yticks(yticks, crs=crs)
        lat_formatter = LatitudeFormatter()
        plt_ax.yaxis.set_major_formatter(lat_formatter)

    if grid:
        if xticks is not None and yticks is None:
            plt_ax.gridlines(xlocs=xticks)
        elif xticks is None and yticks is not None:
            plt_ax.gridlines(ylocs=yticks)
        elif xticks is None and yticks is None:
            plt_ax.gridlines()
        elif xticks is not None and yticks is not None:
            plt_ax.gridlines(xlocs=xticks, ylocs=yticks)

    if feature_list is not None:
        for f in feature_list:
            plt_ax.add_feature(f)

    if extent is not None:
        plt_ax.set_extent(extent, crs=crs)

def format_axes(axes, **kwargs):
    """Format one or more axes.
    Passes all arguments to _format_axis
    """
    if isinstance(axes, np.ndarray):
        # There are multiple axes, format each of them
        for ax in axes.flat:
            _format_axis(ax, **kwargs)
    else:
        # There is just one
        _format_axis(axes, **kwargs)

def get_row_col(i, axes):
    """Get the ith element of axes
    """
    if isinstance(axes, np.ndarray):
        # it contains subplots
        if len(axes.shape) == 1:
            return axes[i]
        elif len(axes.shape) == 2:
            nrow = axes.shape[0]
            ncol = axes.shape[1]
            row_i = i // ncol
            col_i = i - (row_i * ncol)
            return axes[row_i, col_i]
        else:
            ValueError('This is a 3-dimensional subplot, this function can only handle 2D')
    else:
        return axes
