import csv
from math import *

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
# # Calculate centroid of the core samples of each cluster
def get_cluster_centroids(lst):
    cluster_nums = []
    cluster_centroids = []
    for row in lst:
        if row[3] not in cluster_nums and row[3]!="-1":
            cluster_nums.append(row[3])
    for num in cluster_nums:
        total_lat = 0
        total_lon = 0
        cluster_lst = list(filter(lambda x: x[3] == num, lst))
        total_in_cluster = len(cluster_lst)
        for row in cluster_lst:
            total_lat += float(row[1])
            total_lon += float(row[2])
        cluster_centroids.append([num, total_lat/total_in_cluster, total_lon/total_in_cluster])
    return cluster_centroids


##############################################################################
# # Algorithm to extract routes
def get_cluster_num(row):
    return row[3]

def is_core(row):
    if row[4] == "core":
        return True
    return False

def remove_non_cluster_at_list_front(lst):
    copy = lst.copy()
    for row in copy:
        if get_cluster_num(row) == str(-1):
            lst.pop(lst.index(row))
        else:
            break
    return lst

def minutes_difference(row1, row2):
    hour_diff = int(str(row1[0])[11:13])- int(str(row2[0])[11:13])
    min_diff = int(str(row1[0])[14:16]) - int(str(row2[0])[14:16])
    return abs(hour_diff*60 + min_diff)

def different_core_clusters(row1, row2):
    if row1[4] == row2[4] == "core" and row1[3] != row2[3]:
        return True
    return False

def route_is_sufficiently_long(non_core_chunk, min_route_length_for_same_cluster=6):
    if not different_core_clusters(non_core_chunk[0], non_core_chunk[-1]):
        return len(non_core_chunk) >= min_route_length_for_same_cluster
    return True

def cluster_ratios_too_high(non_core_chunk):          # To weed out 'fake' routes which are actually just a person staying in one cluster
    num_of_cluster_pts = 0
    if get_cluster_num(non_core_chunk[0]) == get_cluster_num(non_core_chunk[-1]):
        for row in non_core_chunk:
            if get_cluster_num(row) == get_cluster_num(non_core_chunk[0]):
                num_of_cluster_pts += 1
        if num_of_cluster_pts/len(non_core_chunk) > 0.6:
            return True
    return False

def consecutive_rows(lst, row1, row2):
    return abs(lst.index(row1) - lst.index(row2)) == 1

def extract_route(lst, min_route_length_for_same_cluster=6):
    non_core_chunks = []
    non_core_chunk = []
    building_chunk = False       #checks whether a chunk is in the midst of being formed
    for i in range(len(lst)):
        if not is_core(lst[i]):     #for non-core samples
            if not building_chunk and i!= 0:                
                non_core_chunk.extend([lst[i-1], lst[i]])
                building_chunk = True
            elif not building_chunk and i==0:
                non_core_chunk.append(lst[i])
                building_chunk = True
            elif i == len(lst)-1:
                non_core_chunk.append(lst[i])
                if route_is_sufficiently_long(non_core_chunk, min_route_length_for_same_cluster) and not cluster_ratios_too_high(non_core_chunk):
                    non_core_chunks.append(non_core_chunk)
            else:
                non_core_chunk.append(lst[i])
        else:                        #for core samples
            if not building_chunk:
                if different_core_clusters(lst[i-1], lst[i]) and is_core(lst[i]):   #to cater for scenarios with no routes in between clusters
                    non_core_chunks.append([lst[i-1], lst[i]])
                continue
            elif i == len(lst)-1:         #if chunk is in progress of being formed and this is the last row
                non_core_chunk.append(lst[i])
                if route_is_sufficiently_long(non_core_chunk, min_route_length_for_same_cluster) and not cluster_ratios_too_high(non_core_chunk):
                    non_core_chunks.append(non_core_chunk)
            elif not is_core(lst[i+1]) and minutes_difference(lst[i], lst[i+1]) <= 10:    # if next row is a non-core sample & duration between this
                non_core_chunk.append(lst[i])                                             # and next sample is less than 10min
            else:
                non_core_chunk.append(lst[i])
                building_chunk = False
                if non_core_chunks != [] and minutes_difference(non_core_chunks[-1][-1], non_core_chunk[0]) <= 2 and not cluster_ratios_too_high(non_core_chunk):
                    if not consecutive_rows(lst, non_core_chunks[-1][-1], non_core_chunk[0]):
                        non_core_chunks[-1].append(lst[i-len(non_core_chunk)])
                    non_core_chunks[-1].extend(non_core_chunk)
                elif route_is_sufficiently_long(non_core_chunk, min_route_length_for_same_cluster) and not cluster_ratios_too_high(non_core_chunk):
                    non_core_chunks.append(non_core_chunk)
                non_core_chunk = []
    return non_core_chunks

##############################################################################
## Clean detected routes (1)
def trim_half_hourly_intervals(route):
    no_of_intervals = len(route)-1
    #bprint("-------")
    #print(no_of_intervals)
    for i in range(int(no_of_intervals/2)):
        if minutes_difference(route[0], route[1]) == 30:
            route = route[1:]
            #print(route)
        if minutes_difference(route[-1], route[-2]) == 30:
            route = route[:-1]
            #print(route)
    remove_non_cluster_at_list_front(route)
    route.reverse()
    remove_non_cluster_at_list_front(route)
    route.reverse()
    if len(route) <= 3:
        return None
    return route

##############################################################################
## Clean detected routes (2)
def get_latlong_from_routes(route_lst):     
    route_latlngs = []
    for r in route_lst:
        route_latlngs.append([float(r[1]), float(r[2])])
    return route_latlngs

# convert lat-longs to (x,y) vectors
def calculate_xy(lat,lon):
    globe_radius = 6371000 #in meter
    lon0 = 103.8
    x = globe_radius * (lon-lon0)/180 * pi
    y = globe_radius * log(tan(pi/4 + lat/2 * pi/180 ))
    return [x, y]

# xy = calculate_xy(1.320250725, 103.7670256)
# print(xy)

def get_vector_between_points(lat1, lon1, lat2, lon2):  #pt1 -> pt2
    xy_1 = calculate_xy(lat1, lon1)
    xy_2 = calculate_xy(lat2, lon2)
    vector = [xy_2[0]-xy_1[0], xy_2[1]-xy_1[1]]
    return vector

def dot_product(vector1, vector2):
    result = vector1[0]*vector2[0] +vector1[1]*vector2[1]
    return result

def negative_dot_product_percentage(route_lst, min_route_length_for_same_cluster=6):
    route_latlngs = get_latlong_from_routes(route_lst)
    negative_dot_product_count = 0
    indexes_to_pop = []
    for i in range(len(route_lst)-1):
        v = get_vector_between_points(route_latlngs[i][0], route_latlngs[i][1], route_latlngs[i+1][0], route_latlngs[i+1][1])
        if -10.0 <= v[0] <= 10.0 and -10.0 <= v[1] <= 10.0:
            # print(v)
            indexes_to_pop.append(i+1)
    indexes_to_pop.reverse()
    for i in indexes_to_pop:
        route_latlngs.pop(i)
    # print(len(route_latlngs))
    if len(route_latlngs) < min_route_length_for_same_cluster and not different_core_clusters(route_lst[0], route_lst[-1]):
        return

    for i in range(len(route_latlngs)-2):
        vector1 = get_vector_between_points(route_latlngs[i][0], route_latlngs[i][1], route_latlngs[i+1][0], route_latlngs[i+1][1])
        vector2 = get_vector_between_points(route_latlngs[i+1][0], route_latlngs[i+1][1], route_latlngs[i+2][0], route_latlngs[i+2][1])
        #print(dot_product(vector1, vector2))
        #print(dot_product(vector1, vector2))
        if dot_product(vector1, vector2) < 0:
            negative_dot_product_count += 1
    result = negative_dot_product_count/(len(route_latlngs)-2)
    return result

##############################################################################
if __name__ == "__main__":
    data = read_csv("gpeh_minutes_17032016_clustered.csv")
    remove_non_cluster_at_list_front(data)      ## Removes non-cluster points at beginning. route must begin at a cluster
    data.reverse()
    remove_non_cluster_at_list_front(data)      ## Removes non-cluster points at ending. route must end in a cluster
    data.reverse()
    if data != []:
        start_time = data[0][0]
        end_time = data[-1][0]
    centroids = get_cluster_centroids(data[1:])
    print(centroids)
    routes = extract_route(data[1:])
    # print("--------")
    # for route in routes:
    #     if not different_core_clusters(route[0], route[-1]):
    #         route = trim_half_hourly_intervals(route)
    #     if route != None:
    #         neg_percentage = negative_dot_product_percentage(route)
    #         if neg_percentage == None:
    #             continue
    #         else:
    #             print("neg_percentage: "+str(neg_percentage))
    #             print("num_of_points_above_speed_threshold: "+str(num_of_points_above_speed_threshold(route)))
    #             print(route)













