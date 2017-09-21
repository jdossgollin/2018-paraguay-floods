import numpy as np
# Specify some parameters for plotting
# this will keep the layout and look the same

# Define color maps
cmap = {'psi': 'PuOr', 'psi_a': 'PuOr', 'rain': 'Greens', 'rain_a': 'BrBG'}

# Some extents for plotting
extent = {'SAm': [275, 330, 5, -45], 'SH': [-140,10,-60,10]}

# Some levels
levels = {'psi': np.linspace(-2.4e7, 2.4e7, 13), 'psi_a': np.linspace(-3.5e6, 3.5e6, 8)}
