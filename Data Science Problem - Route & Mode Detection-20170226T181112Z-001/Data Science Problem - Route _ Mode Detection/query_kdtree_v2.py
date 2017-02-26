import pickle
from scipy import spatial
import numpy
import collections

def open_pickle(filename):
    with open(filename, 'rb') as handle:
        item = pickle.load(handle)
    return item

######################
## KDTree functions ##
######################

# Query KDTree based on k nearest neighbours
def query_kdtree(tree, route, k=1):
    return tree.query(route, k)

# Query KDTree for all points within distance r of point(s) x.
def query_ball_point_kdtree(tree, route, r=0.0025):
    return tree.query_ball_point(route, r)

##########
## Misc ##
##########

# Returns a list of timestamps of the route.
def get_timestamp_from_routes(route_lst):
    route_timestamps = []
    for r in route_lst:
        route_timestamps.append(r[:4])
    return route_timestamps

# Returns a list of lists of lat-longs of the route.
def get_latlong_from_routes(route_lst):     
    route_latlngs = []
    for r in route_lst:
        route_latlngs.append([float(r[1]), float(r[2])])
    return route_latlngs

# Returns a list of node ID and descriptions of nearest nodes, based on nearest node indexes from output of KDTree query.
def get_nearest_node_descriptions(descriptions_list, nearest_nodes_index):
    nearest_nodes_descriptions = []
    for i in nearest_nodes_index:
        if type(i) == numpy.int64:
            nearest_nodes_descriptions += [descriptions_list[i],]
        else:  #i is of type numpy.ndarray
            for j in i:
                nearest_nodes_descriptions += [descriptions_list[j],]
    nearest_nodes_descriptions = list(flatten(nearest_nodes_descriptions))
    result = []
    for item in nearest_nodes_descriptions:
        description = item['k'] + " = " + item['v']
        if description not in result:
            result.append(description)
    return result


def get_description_counts(nearest_nodes_descriptions):
    description_counts = {}
    for tag in nearest_nodes_descriptions:
        if tag in description_counts:
            description_counts[tag] += 1
        else:
            description_counts[tag] = 1
    return description_counts

# Flattens an irregular list of lists
def flatten(l):
    basestring = (str, bytes)
    for el in l:
        if isinstance(el, collections.Sequence) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el



###################
## Main Function ##
###################
def process(kdtree_pickle_filename, descriptions_pickle_filename, route_lst, query_type, k_r):
    timestamps = get_timestamp_from_routes(route_lst)
    route = get_latlong_from_routes(route_lst)
    kdtree = open_pickle(kdtree_pickle_filename)
    descriptions_list = open_pickle(descriptions_pickle_filename)
    all_nearest_nodes_descriptions = []
    if query_type == "query":
        for point in route:
            nearest_nodes_index = query_kdtree(kdtree, [point], k_r)[1]
            nearest_nodes_distinct_descriptions = get_nearest_node_descriptions(descriptions_list, nearest_nodes_index)
            all_nearest_nodes_descriptions.append(nearest_nodes_distinct_descriptions)
    elif query_type == "query_ball_point":
        for point in route:
            nearest_nodes_index = query_ball_point_kdtree(kdtree, [point], k_r)
            nearest_nodes_distinct_descriptions = get_nearest_node_descriptions(descriptions_list, nearest_nodes_index)
            all_nearest_nodes_descriptions.append(nearest_nodes_distinct_descriptions)
    description_counts = get_description_counts(list(flatten(all_nearest_nodes_descriptions)))
    sorted_description_counts = sorted(description_counts.items(), key=lambda x:x[1], reverse=True)
    # for x in sorted_description_counts:
    #     while True:
    #         try:
    #             print(x)
    #             break
    #         except:
    #             print(x[0].encode('utf-8'))
    #             print(x[1])
    #             break
    return [sorted_description_counts, all_nearest_nodes_descriptions, timestamps]

############################ Test ################################
# kdtree = open_pickle("lat_long_kdtree.pickle")
# descriptions_list = open_pickle("descriptions_list.pickle")
# route_lst = [['2016-03-14 07:06', '1.3233600223081028', '103.76461889594793', '0', 'core'], ['2016-03-14 07:08', '1.3180506592921482', '103.76874078065157', '0', 'non-core'], ['2016-03-14 07:14', '1.3133589248117155', '103.76519858837128', '-1', 'non-core'], ['2016-03-14 07:15', '1.313254047845004', '103.77396080642939', '-1', 'non-core'], ['2016-03-14 07:16', '1.3107311125736218', '103.77748650631735', '-1', 'non-core'], ['2016-03-14 07:17', '1.3093012459868503', '103.78272084519267', '-1', 'non-core'], ['2016-03-14 07:18', '1.3083076183772913', '103.78953393548727', '-1', 'non-core'], ['2016-03-14 07:19', '1.306826212158573', '103.79145031794906', '-1', 'non-core'], ['2016-03-14 07:20', '1.3051378657857153', '103.79872865974903', '-1', 'non-core'], ['2016-03-14 07:21', '1.3005383429708492', '103.80110658418674', '-1', 'non-core'], ['2016-03-14 07:22', '1.2962636053632015', '103.80532130599022', '-1', 'non-core'], ['2016-03-14 07:23', '1.2932369947481046', '103.8084176927805', '-1', 'non-core'], ['2016-03-14 07:24', '1.29078180774499', '103.81220812350512', '-1', 'non-core'], ['2016-03-14 07:25', '1.2881611487344113', '103.81658770143986', '-1', 'non-core'], ['2016-03-14 07:26', '1.288461144678111', '103.82171373814344', '-1', 'non-core'], ['2016-03-14 07:29', '1.2820405467287337', '103.83914541453123', '1', 'non-core'], ['2016-03-14 07:30', '1.2827013217161618', '103.83687280118465', '-1', 'non-core'], ['2016-03-14 07:31', '1.2786948784713894', '103.84327869862318', '1', 'core']]
# route = get_latlong_from_routes(route_lst)
# #nearest_nodes_index = query_kdtree(kdtree, route, 4)[1]
# nearest_nodes_index = query_ball_point_kdtree(kdtree, route, 0.0025)
# nearest_nodes_descriptions = get_nearest_node_descriptions(descriptions_list, nearest_nodes_index)
# nearest_nodes_descriptions = list(flatten(nearest_nodes_descriptions))

# description_counts = get_description_counts(nearest_nodes_descriptions)
# sorted_description_counts = sorted(description_counts.items(), key=lambda x:x[1], reverse=True)

# for x in sorted_description_counts:
#     while True:
#         try:
#             print(x)
#             break
#         except:
#             print(x[0].encode('utf-8'))
#             print(x[1])
#             break

##################### Main Function Run ##########################
if __name__== "__main__":
    # ACF
    #route_lst = [['2016-03-14 07:06', '1.3233600223081028', '103.76461889594793', '0', 'core'], ['2016-03-14 07:08', '1.3180506592921482', '103.76874078065157', '0', 'non-core'], ['2016-03-14 07:14', '1.3133589248117155', '103.76519858837128', '-1', 'non-core'], ['2016-03-14 07:15', '1.313254047845004', '103.77396080642939', '-1', 'non-core'], ['2016-03-14 07:16', '1.3107311125736218', '103.77748650631735', '-1', 'non-core'], ['2016-03-14 07:17', '1.3093012459868503', '103.78272084519267', '-1', 'non-core'], ['2016-03-14 07:18', '1.3083076183772913', '103.78953393548727', '-1', 'non-core'], ['2016-03-14 07:19', '1.306826212158573', '103.79145031794906', '-1', 'non-core'], ['2016-03-14 07:20', '1.3051378657857153', '103.79872865974903', '-1', 'non-core'], ['2016-03-14 07:21', '1.3005383429708492', '103.80110658418674', '-1', 'non-core'], ['2016-03-14 07:22', '1.2962636053632015', '103.80532130599022', '-1', 'non-core'], ['2016-03-14 07:23', '1.2932369947481046', '103.8084176927805', '-1', 'non-core'], ['2016-03-14 07:24', '1.29078180774499', '103.81220812350512', '-1', 'non-core'], ['2016-03-14 07:25', '1.2881611487344113', '103.81658770143986', '-1', 'non-core'], ['2016-03-14 07:26', '1.288461144678111', '103.82171373814344', '-1', 'non-core'], ['2016-03-14 07:29', '1.2820405467287337', '103.83914541453123', '1', 'non-core'], ['2016-03-14 07:30', '1.2827013217161618', '103.83687280118465', '-1', 'non-core'], ['2016-03-14 07:31', '1.2786948784713894', '103.84327869862318', '1', 'core']]

    # CAF 18
    route_lst = [['2016-03-18 08:17', '1.3880628382205689', '103.85337347963026', '0', 'core'], ['2016-03-18 08:18', '1.3775774335033717', '103.85768260806799', '-1', 'non-core'], ['2016-03-18 08:19', '1.371398836908549', '103.86183924973011', '-1', 'non-core'], ['2016-03-18 08:20', '1.3620945621542', '103.8593826815486', '-1', 'non-core'], ['2016-03-18 08:21', '1.356866841193967', '103.85880779474974', '-1', 'non-core'], ['2016-03-18 08:22', '1.35106371769912', '103.85669510811567', '-1', 'non-core'], ['2016-03-18 08:23', '1.3549971528584457', '103.85901079326868', '-1', 'non-core'], ['2016-03-18 08:29', '1.3497891284453034', '103.84280394762754', '-1', 'non-core'], ['2016-03-18 08:30', '1.3482985904395632', '103.84318482130766', '-1', 'non-core'], ['2016-03-18 08:31', '1.3550765232662236', '103.84150441735983', '-1', 'non-core'], ['2016-03-18 08:32', '1.3503160666946463', '103.8407179553594', '-1', 'non-core'], ['2016-03-18 08:33', '1.3476797060365975', '103.83887853473425', '-1', 'non-core'], ['2016-03-18 08:34', '1.3447697521571662', '103.8376303575933', '-1', 'non-core'], ['2016-03-18 08:37', '1.3372303647733037', '103.81924498826265', '-1', 'non-core'], ['2016-03-18 08:38', '1.32480735596099', '103.81489539518952', '-1', 'non-core'], ['2016-03-18 08:39', '1.3196439158851598', '103.81351771205664', '-1', 'non-core'], ['2016-03-18 08:40', '1.3143761049599896', '103.80380988121033', '-1', 'non-core'], ['2016-03-18 08:41', '1.308331992741845', '103.80167338997126', '-1', 'non-core'], ['2016-03-18 08:42', '1.302714668149009', '103.80193818360567', '-1', 'non-core'], ['2016-03-18 08:43', '1.3001457758586572', '103.79947330802679', '-1', 'non-core'], ['2016-03-18 08:44', '1.2965489645218338', '103.79940245300531', '-1', 'non-core'], ['2016-03-18 08:45', '1.2903948617861454', '103.80093240941113', '1', 'non-core'], ['2016-03-18 08:46', '1.2947961422001606', '103.80497004836798', '1', 'non-core'], ['2016-03-18 08:47', '1.289220183955125', '103.80443997681141', '1', 'core']]

    #CAF 14
    #route_lst = [['2016-03-14 12:01', '1.3898775863695354', '103.85576706379652', '0', 'core'], ['2016-03-14 12:03', '1.3633832185081631', '103.85932317003608', '-1', 'non-core'], ['2016-03-14 12:04', '1.347962766140173', '103.85969616472721', '-1', 'non-core'], ['2016-03-14 12:05', '1.3398783498677918', '103.86001098901033', '-1', 'non-core'], ['2016-03-14 12:06', '1.3443944588189953', '103.86783499270678', '-1', 'non-core'], ['2016-03-14 12:07', '1.3202721904806627', '103.85644347220659', '-1', 'non-core'], ['2016-03-14 12:08', '1.314231306994999', '103.84620152413845', '-1', 'non-core'], ['2016-03-14 12:09', '1.3047074829731766', '103.84308222681284', '-1', 'non-core'], ['2016-03-14 12:11', '1.2779786841891019', '103.8392647728324', '-1', 'non-core'], ['2016-03-14 12:12', '1.2803039153430866', '103.83615408092737', '-1', 'non-core'], ['2016-03-14 12:13', '1.277625052946498', '103.82928913459182', '-1', 'non-core'], ['2016-03-14 12:14', '1.2808673737679876', '103.82347863167524', '-1', 'non-core'], ['2016-03-14 12:16', '1.2718185050904263', '103.82114510983229', '1', 'non-core'], ['2016-03-14 12:17', '1.2693715911810888', '103.82284495979548', '1', 'non-core'], ['2016-03-14 12:18', '1.2660826646397687', '103.82673047482967', '-1', 'non-core'], ['2016-03-14 12:19', '1.2694687972152665', '103.82518719881773', '-1', 'non-core'], ['2016-03-14 12:21', '1.2659342791961858', '103.82406245917082', '1', 'non-core'], ['2016-03-14 12:22', '1.2562728529154779', '103.82206879556179', '1', 'core']]
    

    #process("lat_long_kdtree.pickle", "descriptions_list.pickle", route, "query", 3)
    output = process("lat_long_kdtree.pickle", "descriptions_list.pickle", route_lst, "query_ball_point", 0.0025)
    #print(output[2])
    for x in output[0]:
        while True:
            try:
                print(x)
                break
            except:
                print(x[0].encode('utf-8'))
                print(x[1])
                break



