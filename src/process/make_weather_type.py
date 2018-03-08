#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Calculate Weather Types
"""

import argparse
import os
from collections import OrderedDict
import xarray as xr
import numpy as np
import pandas as pd
from scipy.stats import pearsonr as correl
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from numba import jit

parser = argparse.ArgumentParser() #pylint: disable=C0103
parser.add_argument("--outfile", help="the filename of the data to save")
parser.add_argument("--table", help="the filename of the latex table to write", default=None)
parser.add_argument("--infile", help="the input data")
parser.add_argument("--var_xpl", type=float, help="Min amount of variance that must be retained")
parser.add_argument("--n_cluster", type=int, help="Number of clusters to create")
parser.add_argument("--n_sim", type=int, help="Number of simulations to create")

@jit
def loop_kmeans(X, pc_ts, n_cluster, n_sim, n_components_keep):
    centroids = np.zeros(shape=(n_sim, n_cluster, n_components_keep))
    w_types = np.zeros(shape=(n_sim, X.shape[0]))
    for i in np.arange(n_sim):
        km = KMeans(n_clusters=n_cluster).fit(pc_ts)
        centroids[i, :, :] = km.cluster_centers_
        w_types[i, :] = km.labels_
    return centroids, w_types

@jit
def calc_classifiability(P, Q):
    """Implement the Michaelangeli (1995) Classifiability Index

    The variable naming here is not pythonic but follows the notation in the 1995 paper
    which makes it easier to follow what is going on. You shouldn't need to call
    this function directly but it is called in cluster_xr_eof.

    Args:
        P: a cluster centroid
        Q: another cluster centroid
    """
    k = P.shape[0]
    Aij = np.ones([k, k])
    for i in range(k):
        for j in range(k):
            Aij[i, j], _ = correl(P[i, :], Q[j, :])
    Aprime = Aij.max(axis=0)
    ci = Aprime.min()
    return ci

@jit
def matrix_classifiability(centroids):
    nsim = centroids.shape[0]
    c_pq = np.ones([nsim, nsim])
    for i in range(0, nsim):
        for j in range(0, nsim):
            if i == j:
                c_pq[i, j] = np.nan
            else:
                c_pq[i, j] = calc_classifiability(P=centroids[i, :, :], Q=centroids[j, :, :])
    classifiability = np.nanmean(c_pq)
    best_part = np.where(c_pq == np.nanmax(c_pq))[0][0]
    return classifiability, best_part

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
    new_labels = orders[labels_from[old_labels]] + 1
    return new_labels

def main():
    """Parse the command line arguments and run download_data().
    """
    np.random.seed(1085) # set seed from
    args = parser.parse_args()
    psi = xr.open_dataset(args.infile)['anomaly']

    # carry out PCA
    psi_stacked = psi.stack(grid=['lon', 'lat'])
    pca = PCA().fit(psi_stacked)
    cum_var = pca.explained_variance_ratio_.cumsum()
    n_components_keep = np.where(cum_var > args.var_xpl)[0].min() + 1 #compensate for zero indexing
    pca = PCA(n_components=n_components_keep).fit(psi_stacked)
    pc_ts = pca.transform(psi_stacked)
    loadings = pca.components_

    # Re-Scale the PC Time series to standard normal -- this is not always good
    pc_ts = StandardScaler().fit_transform(pc_ts)

    centroids, wtypes = loop_kmeans(X=psi_stacked, pc_ts=pc_ts, n_cluster=args.n_cluster, n_sim=args.n_sim, n_components_keep=n_components_keep)
    class_idx, best_part = matrix_classifiability(centroids)

    if args.table is not None:
        best_centroid = centroids[best_part, :, :]
        best_centroid = pd.DataFrame(best_centroid)
        best_centroid.columns = ['EOF {}'.format(i) for i in np.arange(1, n_components_keep + 1)]
        best_centroid['WT'] = np.arange(1, args.n_cluster + 1)
        best_centroid.set_index('WT', inplace=True)
        best_centroid.round(decimals=3).to_latex(args.table)

    best_wt = wtypes[best_part, :]
    best_wt = pd.Series(resort_labels(best_wt), index=psi['time']).to_xarray()
    best_wt.name = 'wtype'
    best_wt.attrs = OrderedDict(class_idx = class_idx)

    if os.path.isfile(args.outfile):
        os.remove(args.outfile)
    best_wt.to_netcdf(args.outfile, format='NETCDF4')



if __name__ == "__main__":
    main()
