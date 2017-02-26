# -*- coding: utf-8 -*-
"""
===================================
Demo of DBSCAN clustering algorithm
===================================

Finds core samples of high density and expands clusters from them.

"""
#print(__doc__)

import csv
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler

from merge_overclustered_clusters import *

def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of list
    containing rows in the csv file and its entries.
    """
    rows = []

    with open(csvfilename, "rU") as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows.append(row)
    return rows

def write_csv(newcsvfilename, lst, heading):
    with open(newcsvfilename, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        data = [heading,]
        data.extend(lst)
        writer.writerows(data)
##############################################################################
# # Merge seconds to minutes
def merge_seconds_to_min(data):
    #data = read_csv(raw_gpeh)
    data = sorted(data[1:], key = lambda x: x[0])
    minute_data = []
    current_time = data[1][0][:16]
    count = 1
    lat = float(data[1][5])
    lon = float(data[1][6])
    for i in range(2, len(data)):
        if data[i][0][:16] == current_time:
            lat += float(data[i][5])
            lon += float(data[i][6])
            count += 1
        else:
            minute_data.append([current_time, float(lat)/count, float(lon)/count])
            current_time = data[i][0][:16]
            lat = float(data[i][5])
            lon = float(data[i][6])
            count = 1
    minute_data.append([current_time, float(lat)/count, float(lon)/count])

    #write_csv(new_filename, minute_data, ["Date Time", "Latitude", "Longitude"])
    return minute_data

##############################################################################
def compute_dbscan(data_rows, data_headings, filename):
    #data = read_csv(filename)
    X = []
    for row in data_rows:
        X.append(row[1:3])
    X = StandardScaler().fit_transform(X)

    eps_ = 0.2
    n_clusters_ = 0
    while n_clusters_ <= 1 and eps_<=0.3:
        db = DBSCAN(eps = eps_, min_samples = 10).fit(X)
        # Number of clusters in labels, ignoring noise if present.
        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        eps_ += 0.05

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    data_headings.append("Cluster Number")
    data_headings.append("Core or Non-Core Sample")
    for i in range(len(data_rows)):
        data_rows[i].append(db.labels_[i])
        if i in db.core_sample_indices_:
            data_rows[i].append("core")
        else:
            data_rows[i].append("non-core")
    write_csv(filename, data_rows, data_headings)


    print('\nEstimated number of clusters: %d' % n_clusters_)
    data = merge(filename, n_clusters_)
    return data

##############################################################################
if __name__ == "__main__":
    for i in range(17, 19):
        print("\n------ " + str(i) + " March 2016 ------")
        minute_data = merge_seconds_to_min("gpeh_output_201603"+str(i)+"_52501653ED65B71D13109B43817932AD69E069.csv")
        compute_dbscan(minute_data, ["Date Time", "Latitude", "Longitude"], "gpeh_minutes_"+str(i)+"032016_clustered_2.csv")


##############################################################################
# Plot result
# import matplotlib.pyplot as plt

# # Black removed and is used for noise instead.
# unique_labels = set(labels)
# colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
# for k, col in zip(unique_labels, colors):
#     if k == -1:
#         # Black used for noise.
#         col = 'k'

#     class_member_mask = (labels == k)

#     xy = X[class_member_mask & core_samples_mask]
#     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
#              markeredgecolor='k', markersize=14)

#     xy = X[class_member_mask & ~core_samples_mask]
#     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
#              markeredgecolor='k', markersize=6)

# plt.title('Estimated number of clusters: %d' % n_clusters_)
# plt.show()

