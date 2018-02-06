import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

from pyfloods import region,paths,raw_data


mjo = raw_data.mjo.get_data()['2015-11-01':'2016-02-29']
mjo['month'] = mjo.index.month

# MAKE THE FIGURE
plt.figure(figsize=(7,5))
sns.lmplot(
    x='RMM1', y='RMM2', data=mjo,
    fit_reg=False, hue='month',
    scatter_kws={"marker": "D", "s": 100}, size = 8
)
plt.plot(mjo['RMM1'], mjo['RMM2'], color='gray')
plt.axvline(0, color='gray')
plt.axhline(0, color='gray')
plt.plot((100,-100), (100, -100), color='gray')
plt.plot((-100,100), (100, -100), color='gray')
plt.ylim(-3,3)
plt.xlim(-3,3)
plt.xlabel('RMM1')
plt.ylabel('RMM2')
plt.savefig(os.path.join(paths.figures, 'mjo-time-series.pdf'), bbox_inches='tight')
