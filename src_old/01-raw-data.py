import pandas as pd

from pyfloods.paths import data_external
from pyfloods.raw_data import mjo,enso,topo,sst,s2s,u850,v850,cpc

# save us from pain :)
pd.set_option('display.max_rows', 5)

# Single-File Data Sets
mjo.get_data()
enso.get_data()
topo.get_data()
sst.get_data()
s2s.get_data()

# Multi-File Data Sets
u850.get_data()
v850.get_data()
cpc.get_data()
