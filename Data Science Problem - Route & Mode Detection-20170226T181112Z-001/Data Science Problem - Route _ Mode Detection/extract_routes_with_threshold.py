import sys
sys.path.insert(0, '/Users/nicole/Documents/Predicting_trip_routes_and_type/525016C1DA9D6B108555429A7C41E409B57CAF')

from plot_dbscan import *
from extract_routes import *
from calculate_speed import *

def process(raw_gpeh_list, new_filename, min_route_length_for_different_clusters=4, min_route_length_for_same_cluster=6, eliminate_long_intervals=True, max_negative_dot_product = 0.7, max_speed=150, above_max_speed_max_num = 1):
    minute_data = merge_seconds_to_min(raw_gpeh_list)
    clustered_data = compute_dbscan(minute_data, ["Date Time", "Latitude", "Longitude"], new_filename)
    #Get start time and end time of records
    clustered_data = remove_non_cluster_at_list_front(clustered_data[1:])      ## Removes non-cluster points at beginning. route must begin at a cluster
    clustered_data.reverse()
    clustered_data = remove_non_cluster_at_list_front(clustered_data[1:])      ## Removes non-cluster points at ending. route must end in a cluster
    clustered_data.reverse()
    if clustered_data != []:
        start_time_and_cluster = [clustered_data[0][0], clustered_data[0][3]]
        end_time_and_cluster = [clustered_data[-1][0], clustered_data[-1][3]]
        print('Starting Time of Dataset: '+start_time_and_cluster[0])
        print('Ending Time of Dataset: '+end_time_and_cluster[0])
    else:
        return
    ##########################################################
    # # Calculate Cluster Centroids
    centroids = get_cluster_centroids(clustered_data)
    ##########################################################
    # # Extract Routes
    routes = extract_route(clustered_data, min_route_length_for_same_cluster)
    for route in routes.copy():
        if len(route) == 2:
            continue
        if not different_core_clusters(route[0], route[-1]) and eliminate_long_intervals:
            if trim_half_hourly_intervals(route.copy()) == None:
                # print(route)
                routes.remove(route)
                continue
        neg_percentage = negative_dot_product_percentage(route, min_route_length_for_same_cluster)
        if not different_core_clusters(route[0], route[-1]) and (neg_percentage == None or neg_percentage > max_negative_dot_product):
            #print("neg")
            # print(neg_percentage)
            # print(route)
            routes.remove(route)
            continue
        elif num_of_pairs_above_speed_threshold(route, max_speed) > above_max_speed_max_num:
            #print("speed")
            # print(route)
            routes.remove(route)
            continue

    ##########################################################

    #Time boundaries when user stayed in cluster
    time_boundaries = [start_time_and_cluster]
    for i in range(len(routes)):
        time_boundaries[i].extend([routes[i][0][0],routes[i][0][3]])
        time_boundaries.append([routes[i][-1][0], routes[i][-1][3]])
    time_boundaries[-1].extend(end_time_and_cluster)
    for start_end_times in time_boundaries.copy():
        if start_end_times[1] != start_end_times[3]:
            time_boundaries.remove(start_end_times)
        elif start_end_times[0] == start_time_and_cluster[0] and start_end_times[2] == end_time_and_cluster[0]:
            time_boundaries.remove(start_end_times)
        elif minutes_difference(start_end_times[:2], start_end_times[2:])<=2 and start_end_times[0]!= start_time_and_cluster[0] and start_end_times[0]!= end_time_and_cluster[0]:
            time_boundaries.remove(start_end_times)
        else:
            start_end_times.pop(1)

    for i in range(len(time_boundaries.copy())-1, -1, -1):
        if time_boundaries[i][2] == time_boundaries[i-1][2] and minutes_difference([time_boundaries[i][0]],[time_boundaries[i-1][1]])<=2:
            time_boundaries[i-1][1] = time_boundaries[i][1]
            time_boundaries.remove(time_boundaries[i])

    # print('\nDetected time periods where person stayed within a cluster:')
    # for start_end_times in time_boundaries:
    #     if start_end_times[2] != '-1':
    #         print(start_end_times[0] + ' to ' + start_end_times[1] + '- Cluster ' + start_end_times[2])

    # print("\nRoutes: ")
    for route in routes.copy():
        if len(route) == 2:
            #print(route)
            routes.remove(route)
        elif different_core_clusters(route[0], route[-1]) and len(route) < min_route_length_for_different_clusters:
            #print(route)
            routes.remove(route)
        # else:
        #     print(route)

    return [time_boundaries, routes, centroids]




if __name__ == "__main__":
    # for i in range(14, 19):
    #     print("------")
    #     result = process("gpeh_output_201603"+str(i)+"_525016C1DA9D6B108555429A7C41E409B57CAF.csv", "gpeh_minutes_"+str(i)+"032016_clustered.csv")
    #     for r in result:
    #         print("---")
    #         print(r)
    #     print('\nDetected time periods where person stayed within a cluster:')
    #     for lst in result[0]:
    #         print(lst[0] + ' to ' + lst[1] + '- Cluster ' + lst[2])
    #     print("\nRoutes: ")
    #     for route in result[1]:
    #         print(route)
    raw_gpeh_list = read_csv("gpeh_output_201601_"+"5250167F8F05F34663DA47D0A5A7D64F0333CC.csv")
    result = process(raw_gpeh_list, "5250167F8F05F34663DA47D0A5A7D64F0333CC"+"_clustered.csv")
    for r in result:
        print("---")
        print(r)
    print('\nDetected time periods where person stayed within a cluster:')
    for lst in result[0]:
        print(lst[0] + ' to ' + lst[1] + '- Cluster ' + lst[2])
    print("\nRoutes: ")
    for route in result[1]:
        print(route)




