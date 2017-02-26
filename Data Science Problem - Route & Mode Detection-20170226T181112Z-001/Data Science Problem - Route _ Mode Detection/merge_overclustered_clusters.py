from math import *
import csv
import itertools
import copy

######################################################################
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

######################################################################
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6378137 # Radius of earth in metres
    return round(c * r,4)

def inspect_clusters(cluster1, cluster2):
    no_of_nearby_pts = 0
    for pt1 in cluster1:
        for pt2 in cluster2:
            dist = haversine(float(pt1[1]), float(pt1[2]), float(pt2[1]), float(pt2[2]))
            if dist <=155:
                no_of_nearby_pts +=1
    return no_of_nearby_pts

def get_cluster_centroid(cluster):
    total_lat = 0
    total_lon = 0
    total_in_cluster = len(cluster)
    for pt in cluster:
        total_lat += float(pt[1])
        total_lon += float(pt[2])
    return [total_lat/total_in_cluster, total_lon/total_in_cluster]

def dist_btween_cluster_centroids(cluster1, cluster2):
    cluster1_centroid = get_cluster_centroid(cluster1)
    cluster2_centroid = get_cluster_centroid(cluster2)
    return haversine(cluster1_centroid[0], cluster1_centroid[1], cluster2_centroid[0], cluster2_centroid[1])

def rename_cluster(data, cluster_to_rename, new_cluster_num):
    for row in data:
        if row[3] == str(cluster_to_rename):
            row[3] = str(new_cluster_num)
    return data

def merge(filename, num_of_clusters):
    data = read_csv(filename)
    iterable = range(num_of_clusters)
    renamed_clusters = {}
    data_copy = copy.deepcopy(data)
    for cluster_combi in itertools.combinations(iterable,2):
        cluster1 = list(filter(lambda x: x[3]==str(cluster_combi[0]), data_copy))
        cluster2 = list(filter(lambda x: x[3]==str(cluster_combi[1]), data_copy))
        no_of_nearby_pts = inspect_clusters(cluster1, cluster2)
        centroid_distance = dist_btween_cluster_centroids(cluster1, cluster2)
        if no_of_nearby_pts >=3 and centroid_distance<= 1000:
            if cluster_combi[0] in renamed_clusters.keys():
                data = rename_cluster(data, cluster_combi[1], renamed_clusters[cluster_combi[0]])
                renamed_clusters[cluster_combi[1]] = renamed_clusters[cluster_combi[0]]
                print("cluster " + str(cluster_combi[1]) + " renamed to cluster " +str(renamed_clusters[cluster_combi[0]]))
            elif cluster_combi[1] in renamed_clusters.keys():
                data = rename_cluster(data, cluster_combi[0], renamed_clusters[cluster_combi[1]])
                renamed_clusters[cluster_combi[0]] = renamed_clusters[cluster_combi[1]]
                print("cluster " + str(cluster_combi[0]) + " renamed to cluster " +str(renamed_clusters[cluster_combi[1]]))
            else:
                data = rename_cluster(data, cluster_combi[0], cluster_combi[1])
                renamed_clusters[cluster_combi[0]] = cluster_combi[1]    #{'cluster renamed': 'new cluster no.'}
                print("cluster " + str(cluster_combi[0]) + " renamed to cluster " +str(cluster_combi[1]))
    print("Final no. of clusters: " + str(num_of_clusters-len(renamed_clusters)))
    write_csv(filename, data[1:], data[0])
    return data

if __name__ == "__main__":
    # data = read_csv("gpeh_minutes_14032016_clustered.csv")
    # cluster1 = list(filter(lambda x: x[3]=="0", data))
    # cluster2 = list(filter(lambda x: x[3]=="1", data))
    # print(len(cluster1) + len(cluster2))
    # print(inspect_clusters(cluster1, cluster2))
    # print(inspect_clusters(cluster1, cluster2)/(len(cluster1) + len(cluster2))*100)

    merge("gpeh_minutes_18032016_clustered.csv", 2)