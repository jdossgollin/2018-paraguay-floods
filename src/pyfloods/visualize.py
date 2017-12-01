def _FormatAxis(ax, coast=True, grid=False, border=True, river = False, extent=None, ticks=None, states=None, feature_list=[]):
    import cartopy.feature
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    ax.axes.get_xaxis().set_ticklabels([])
    ax.axes.get_yaxis().set_ticklabels([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    if coast: ax.coastlines()
    if grid: ax.gridlines()
    if border: ax.add_feature(cartopy.feature.BORDERS)
    if river: ax.add_feature(cartopy.feature.RIVERS)
    if ticks is not None:
        from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
        ax.set_xticks(ticks[0], crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.set_yticks(ticks[1], crs=ccrs.PlateCarree())
        lat_formatter = LatitudeFormatter()
        ax.yaxis.set_major_formatter(lat_formatter)
    if len(feature_list) > 0:
        for f in feature_list:
            ax.add_feature(f)
    if states is not None:
        ax.add_feature(states, edgecolor='gray')
    if extent is not None:
        ax.set_extent(extent, crs = ccrs.PlateCarree())

def FormatAxes(axes, states=False, **kwargs):
    import matplotlib.pyplot as plt
    import numpy as np
    import cartopy.feature

    if states:
        states_and_provinces = cartopy.feature.NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines',
            scale='50m', facecolor='none')
    else:
        states_and_provinces=None
    if isinstance(axes, np.ndarray):
      for ax in axes.flat:
        _FormatAxis(ax, states=states_and_provinces, **kwargs)
    else:
      _FormatAxis(axes, states=states_and_provinces, **kwargs)



def SetupAxes(ncol, nax, proj, figsize = [12, 7]):
    import matplotlib.pyplot as plt
    import numpy as np
    nrow = int(np.ceil(nax / ncol))
    fig, axes = plt.subplots(nrows=nrow, ncols=ncol,
                             subplot_kw={'projection': proj},
                             figsize=figsize)
    return(fig, axes)



def GetRowCol(i, axes):
    import numpy as np
    if isinstance(axes, np.ndarray):
      # it contains subplots
      if len(axes.shape) == 1:
        return axes[i]
      elif len(axes.shape) == 2:
        nrow = axes.shape[0];ncol = axes.shape[1]
        row_i = i // ncol
        col_i = i - (row_i * ncol)
        return axes[row_i, col_i]
      else:
        ValueError('This is a 3-dimensional subplot, this function can only handle 2D')
    else:
      return(axes)

cmap = {'psi': 'PuOr', 'psi_a': 'PuOr', 'rain': 'Greens', 'rain_a': 'BrBG'}
