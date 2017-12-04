import xarray as xr # for reading in netcdf files
import numpy as np # for calculations
import sklearn.cluster as cl # k-means implemetation
from eofs.xarray import Eof # EOF implementation that recognizes xarray
import pandas as pd # time series

def ReSort(x):
        '''
        A helper function to re-sort the cluster labels.
        Takes in x, a vector of cluster labels, and re-orders them so that
        the lowest number is the most common, and the highest number
        the least common
        '''
        import numpy as np
        x = np.int_(x)
        x_from = np.unique(x).argsort()
        counts = np.array([np.sum(x == xi) for xi in x_from])
        orders = (-counts).argsort().argsort()
        return(orders[x_from[x]])

def Classifiability(P, Q):
    '''
    The Auto-Correlation function
    '''
    from scipy.stats import pearsonr as correl
    k = P.shape[0]
    assert Q.shape[0] is k, "P and Q must be same k"
    Aij = np.ones([k, k])
    for i in range(k):
        for j in range(k):
            Aij[i,j], _ = correl(P[i,:], Q[j,:])
    Aprime = Aij.max(axis=0)
    classifiability = Aprime.min()
    return(classifiability)

def XrEofCluster(ds, n_clusters=5, prop=0.90, nsim=100, verbose = True, pcscaling=0):
    # DS should be an xarray data array (not dataset!)
    if verbose:
        print('xarray-based classifiability for {} clusters'.format(n_clusters))
        print('Performing EOF decomposition of data for dimension reduction.')

    # EOF Decomposition
    solver = Eof(ds, center=True)
    var_frac = solver.varianceFraction()
    cumvar = np.cumsum(var_frac.values)
    eofs_keep = np.where(cumvar >= prop)[0].min() + 1
    pc = solver.pcs(npcs=eofs_keep, pcscaling=pcscaling) # time series of PC
    if verbose:
        print("Number of EOFs retained is {}".format(eofs_keep))
        print('Carrying out {} k-means simulations...'.format(nsim))

    centroids = np.ones([nsim, n_clusters, pc.shape[1]])
    clusters = np.ones([nsim, pc.shape[0]])
    for i in range(0, nsim):
        centroids[i,:,:], clusters[i, :], _ = cl.k_means(pc, n_clusters=n_clusters, n_init=1)
        clusters[i, :] = ReSort(clusters[i, :])
        clusters[i, :] += 1

    if verbose:
        print('Computing classifiability index for each pair of simulations...')

    c_pq = np.ones([nsim, nsim])
    for i in range(0, nsim):
        for j in range(0, nsim):
            if i == j:
                c_pq[i,j] = np.nan
            else:
                c_pq[i,j] = Classifiability(P = centroids[i,:,:], Q = centroids[j,:,:])
    classifiability = np.nanmean(c_pq)
    best_part = np.where(c_pq == np.nanmax(c_pq))[0][0]
    best_centroid = centroids[best_part,:,:]
    best_ts = clusters[best_part,:]

    cluster_ts = xr.DataArray(
        best_ts,
        coords={'time': ds['time'], 'year_adj': ds['year_adj']},
        dims=['time']
    )

    return(best_centroid, cluster_ts, classifiability)
