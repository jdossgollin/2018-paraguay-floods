import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

import pyfloods.visualize as viz
from pyfloods import weather_type
from pyfloods import paths,region
from pyfloods import raw_data

wt = xr.open_dataarray(paths.file_weather_types).to_dataframe(name='wtype')
mjo = raw_data.mjo.get_data()
enso = raw_data.enso.get_data().resample('1D').ffill()
mrg = wt.join(mjo).join(enso)
mrg.loc[mrg['amplitude'] < 1, 'phase'] =  0
mrg['enso_state'] = 0
mrg.loc[mrg['nino_34'] < -1, 'enso_state'] = -1
mrg.loc[mrg['nino_34'] > 1, 'enso_state'] = 1
mrg.head()


conditional = mrg.groupby(['phase', 'enso_state'])['wtype'].apply(lambda g: g.value_counts() / g.size)
conditional = conditional.to_xarray()
anomaly = conditional - conditional.mean(dim=['level_2'])

# Bootstrap simulations
n_sim = 3000
anomalies = []
for i in np.arange(n_sim):
    wt_seq = np.random.choice(mrg['wtype'], size=mrg.shape[0], replace=True)
    simulated = pd.DataFrame({'wtype': wt_seq, 'phase': mrg['phase'], 'enso_state': mrg['enso_state']})
    conditional = simulated.groupby(['phase', 'enso_state'])['wtype'].apply(lambda g: g.value_counts() / g.size)
    conditional = conditional.to_xarray()
    anomalies.append(conditional - conditional.mean(dim=['level_2']))
anomalies = xr.concat(anomalies, dim='temp')

# Select significant simulations
alpha = 0.10
upper = anomalies.quantile(1-alpha/2, dim='temp')
lower = anomalies.quantile(alpha/2, dim='temp')
significant = np.logical_or((anomaly >= upper), (anomaly <= lower))


# Plot
enso_states = {-1: 'La Niña', 0: 'Neutral', 1: 'El Niño'}
p = anomaly.where(significant).plot(
    x='level_2', y='phase', col='enso_state',
    cmap='PuOr',
    figsize=(12, 5)
)
for i,es in enumerate(enso_states):
    ax = p.axes.flat[i]
    ax.set_title(enso_states.get(i-1, ''))
    ax.set_xlabel('Weather Type')
p.axes[0,0].set_ylabel('MJO Phase')
p.cbar.set_label('Anomalous Probability of Occurrence', rotation=270)
plt.savefig(os.path.join(paths.figures, 'wt-mjo-enso.pdf'), bbox_inches="tight")
