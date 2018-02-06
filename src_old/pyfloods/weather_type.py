"""Python functions for performing weather typing
"""

import xarray as xr # for reading in netcdf files
import numpy as np # for calculations
import sklearn.cluster as cl # k-means clustering
from eofs.xarray import Eof # EOF implementation that recognizes xarray
from numba import jit # this massively speeds up the classifiability index
from scipy.stats import pearsonr as correl

def resort_labels(old_labels):
    """Re-sort cluster labels

    Takes in x, a vector of cluster labels, and re-orders them so that
    the lowest number is the most common, and the highest number
    the least common

    Args:
        old_labels: the previous labels of the clusters
    Returns:
        new_labels: the new cluster labels, ranked by frequency of occurrence
    """
    old_labels = np.int_(old_labels)
    labels_from = np.unique(old_labels).argsort()
    counts = np.array([np.sum(old_labels == xi) for xi in labels_from])
    orders = counts.argsort()[::-1].argsort()
    new_labels = orders[labels_from[old_labels]]
    return new_labels

@jit
def calc_classifiability(P, Q): #pylint: disable=C0103
    """Implement the Michaelangeli (1995) Classifiability Index

    The variable naming here is not pythonic but follows the notation in the 1995 paper
    which makes it easier to follow what is going on. You shouldn't need to call
    this function directly but it is called in cluster_xr_eof.

    Args:
        P: a cluster centroid
        Q: another cluster centroid
    """
    k = P.shape[0]
    assert Q.shape[0] is k, "P and Q must be same k"
    Aij = np.ones([k, k]) #pylint: disable=C0103
    for i in range(k):
        for j in range(k):
            Aij[i, j], _ = correl(P[i, :], Q[j, :])
    Aprime = Aij.max(axis=0) #pylint: disable=C0103
    classifiability = Aprime.min()
    return classifiability

def cluster_xr_eof(data_array, n_clusters=5, prop=0.90, nsim=100, verbose=True, pcscaling=0):
    """Carry out k-means clustering on EOFs of an xarray data array

    Args:
        data_array: the xarray data array (not dataset!) on which to cluster
        n_clusters: the number of clusters to create
        prop: the proportion of variance to retain in the EOF decomposition
        nsim: the number of simulations to run and compare
        verbose: if True, print out info at each step
        pcscaling: re-scale PCs? see eofs.xarray.Eof for more details
    """
    if verbose:
        print('xarray-based classifiability for {} clusters'.format(n_clusters))
        print('Performing EOF decomposition of data for dimension reduction.')

    # EOF Decomposition
    solver = Eof(data_array, center=True)
    var_frac = solver.varianceFraction()
    cumvar = np.cumsum(var_frac.values)
    eofs_keep = np.where(cumvar >= prop)[0].min() + 1
    pc_ts = solver.pcs(npcs=eofs_keep, pcscaling=pcscaling) # time series of PC
    if verbose:
        print("Number of EOFs retained is {}".format(eofs_keep))
        print('Carrying out {} k-means simulations...'.format(nsim))

    centroids = np.ones([nsim, n_clusters, pc_ts.shape[1]])
    clusters = np.ones([nsim, pc_ts.shape[0]])
    for i in np.arange(nsim):
        centroids[i, :, :], clusters[i, :], _ = cl.k_means(pc_ts, n_clusters=n_clusters, n_init=1)
        clusters[i, :] = resort_labels(clusters[i, :])
        clusters[i, :] += 1

    if verbose:
        print('Computing classifiability index for each pair of simulations...')
    c_pq = np.ones([nsim, nsim])
    for i in range(0, nsim):
        for j in range(0, nsim):
            if i == j:
                c_pq[i, j] = np.nan
            else:
                c_pq[i, j] = calc_classifiability(P = centroids[i, :, :], Q = centroids[j, :, :])
    classifiability = np.nanmean(c_pq)
    best_part = np.where(c_pq == np.nanmax(c_pq))[0][0]
    best_centroid = centroids[best_part, :, :]
    best_ts = clusters[best_part, :]

    cluster_ts = xr.DataArray(
        best_ts,
        coords={'time': data_array['time'], 'year_adj': data_array['year_adj']},
        dims=['time']
    )

    return best_centroid, cluster_ts, classifiability
