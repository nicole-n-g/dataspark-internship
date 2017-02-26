from math import *

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

def get_lat(row):
    return float(row[1])

def get_lon(row):
    return float(row[2])

def minutes_difference(row1, row2):
    hour_diff = int(str(row1[0])[11:13])- int(str(row2[0])[11:13])
    min_diff = int(str(row1[0])[14:16]) - int(str(row2[0])[14:16])
    return abs(hour_diff*60 + min_diff)

def get_speed_between_points(row1, row2):
    "gets speed between two points in km/hr"
    distance = haversine(get_lat(row1), get_lon(row1), get_lat(row2), get_lon(row2))/1000
    time = minutes_difference(row1, row2)/60
    return distance/time

# def num_of_points_above_speed_threshold(route):
#     count = 0
#     for i in range(len(route)-1):
#         if get_speed_between_points(route[i], route[i+1]) > 150:
#             print(get_speed_between_points(route[i], route[i+1]))
#             count += 1
#     return count


def num_of_pairs_above_speed_threshold(route, speed_threshold):
    count = 0
    for i in range(len(route)-1):
        #print(get_speed_between_points(route[i], route[i+1]))
        if get_speed_between_points(route[i], route[i+1]) > speed_threshold:
            count += 1
    return count

if __name__ == "__main__":
#a = get_speed_between_points(['2016-03-16 06:59', '1.336592487433144', '103.7217716127634', '0', 'core'], ['2016-03-16 07:16', '1.3457906143234872', '103.72162375599146', '-1', 'non-core'])
#print(a)
#route = [['2016-03-16 11:48', '1.275266973852415', '103.79862796515226', '1', 'core'], ['2016-03-16 12:33', '1.268248021157842', '103.82145088165998', '-1', 'non-core'], ['2016-03-16 12:38', '1.271990124196529', '103.81740678101778', '-1', 'non-core'], ['2016-03-16 12:42', '1.2654377531891785', '103.82137980312109', '-1', 'non-core'], ['2016-03-16 12:44', '1.2654708256987528', '103.82132638245821', '-1', 'non-core'], ['2016-03-16 12:47', '1.2635432339897692', '103.82200676947832', '-1', 'non-core'], ['2016-03-16 12:48', '1.2635432339897692', '103.82200676947832', '-1', 'non-core'], ['2016-03-16 12:59', '1.263651837038554', '103.82219385355711', '-1', 'non-core'], ['2016-03-16 13:02', '1.263651837038554', '103.82219385355711', '-1', 'non-core'], ['2016-03-16 14:06', '1.2748137927653742', '103.79889015108347', '1', 'core']]

#route = [['2016-03-18 06:59', '1.3398390862939116', '103.72166331857443', '0', 'core'], ['2016-03-18 07:11', '1.3232313035357999', '103.70428394526243', '-1', 'non-core'], ['2016-03-18 07:12', '1.3224637288185908', '103.70155245065689', '-1', 'non-core'], ['2016-03-18 07:13', '1.3176511158587714', '103.69327113032341', '-1', 'non-core'], ['2016-03-18 07:19', '1.3237528610903297', '103.69782585650682', '-1', 'non-core'], ['2016-03-18 07:24', '1.3215030872908407', '103.69479294866323', '-1', 'non-core'], ['2016-03-18 07:29', '1.3245918273433757', '103.70034076273441', '-1', 'non-core'], ['2016-03-18 07:30', '1.3338580475009805', '103.71698420494795', '0', 'core']]
#route = [['2016-03-15 11:44', '1.2749666408332356', '103.79878219217062', '1', 'core'], ['2016-03-15 11:54', '1.3026735540626049', '103.76525390893221', '-1', 'non-core'], ['2016-03-15 11:57', '1.303734093337005', '103.76622218638659', '-1', 'non-core'], ['2016-03-15 12:08', '1.3036911891019496', '103.76618128269911', '-1', 'non-core'], ['2016-03-15 12:12', '1.3036911891019496', '103.76618128269911', '-1', 'non-core'], ['2016-03-15 12:29', '1.3037434786383275', '103.76624900847673', '-1', 'non-core'], ['2016-03-15 12:51', '1.2831332730600398', '103.78165293484926', '-1', 'non-core'], ['2016-03-15 13:00', '1.2750899918989202', '103.79891630262136', '1', 'core']]
    
    route=[['2016-03-16 17:24', '1.2937631895845316', '103.8563492372632', '2', 'core'], ['2016-03-16 17:25', '1.2831504785224637', '103.84925253689289', '1', 'core']]

    print(len(route))
    num = num_of_pairs_above_speed_threshold(route, 115)
    print(num)
    num = get_speed_between_points(route[0], route[1])
    print(num)