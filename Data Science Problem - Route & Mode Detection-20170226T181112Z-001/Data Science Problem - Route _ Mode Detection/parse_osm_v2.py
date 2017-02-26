import xml.etree.ElementTree as ET
from itertools import islice
import pickle
import collections
from scipy import spatial

def make_elem_tree(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def get_tag_description(tag_lst):
    desired_tags = ["name", "ref", "location", "addr:street", "asset_ref"] #removed "route_ref", "network" and "route"
    tag_attributes = []
    for tag in tag_lst:
        if tag.get('k') in desired_tags:
            tag_attributes.append(tag.attrib)
    return tag_attributes

def parse_nodes(root):
    nodes_dict = {}
    for node in root.findall('node'):
        node_id = node.get('id')
        lat = node.get('lat')
        lon = node.get('lon')       
        tags = node.findall('tag')
        nodes_dict[node_id] = [float(lat), float(lon), get_tag_description(tags)]
    return nodes_dict

def get_ref_id(lst):
    ids = []
    for obj in lst:
        ids.append(obj.get('ref'))
    return ids

def match_way_to_nodes(nodes_dict, way_id, way_description, nodes_in_way):
    node_ids = get_ref_id(nodes_in_way)
    nodes_dict["way_id " + way_id] = node_ids
    for id_ in node_ids:
        if id_ in nodes_dict and way_description not in nodes_dict[id_]:
            nodes_dict[id_].append(way_description)
    return nodes_dict

def parse_ways(root, nodes_dict):
    for way in root.findall('way'):
        way_id = way.get('id')
        nodes_in_way = way.findall('nd')
        if len(nodes_in_way) <= 1:
            continue
        tags = way.findall('tag')
        nodes_dict = match_way_to_nodes(nodes_dict, way_id, get_tag_description(tags), nodes_in_way)
    return nodes_dict

def match_rel_to_nodes(nodes_dict, rel_id, rel_description, nodes_in_rel, ways_in_rel):
    node_ids = get_ref_id(nodes_in_rel)
    way_ids = get_ref_id(ways_in_rel)
    for i in range(len(way_ids)):
        way_ids[i] = "way_id " + way_ids[i]
    for id_ in node_ids:
        if id_ in nodes_dict and rel_description not in nodes_dict[id_]:
            nodes_dict[id_].append(rel_description)
    for id_ in way_ids:
        if id_ in nodes_dict:
            for node in nodes_dict[id_]:
                if node in nodes_dict and rel_description not in nodes_dict[node]:
                    nodes_dict[node].append(rel_description)

def parse_relations(root, nodes_dict):
    for rel in root.findall('relation'):
        rel_id = rel.get('id')
        nodes_in_rel = rel.findall("./member[@type='node']")
        ways_in_rel = rel.findall("./member[@type='way']")
        if len(nodes_in_rel) + len(ways_in_rel) <=1:
            continue
        tags = rel.findall('tag')
        match_rel_to_nodes(nodes_dict, rel_id, get_tag_description(tags), nodes_in_rel, ways_in_rel)
    return nodes_dict

###########################################################
## KDTree
def make_kdtree(lat_lon_lst):
    kdtree = spatial.KDTree(lat_lon_lst)
    return kdtree

###########################################################
## Misc
def split_dict(lat_lon_lst, description_lst, nodes_dict):
    "Splits nodes_dict into two lists - one for lat-longs and the other for descriptions"
    for key, value in nodes_dict.items():
        if key[:6] == "way_id":
            continue
        lat_lon_lst.append(value[:2])
        description_lst.append(list(flatten(value[2:])))

def save_as_pickle(obj, filename):
    "Saves an object in pickle file"
    with open(filename, 'wb') as handle:
        pickle.dump(obj, handle)

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def flatten(l):
    "Flattens an irregular list of lists"
    basestring = (str, bytes)
    for el in l:
        if isinstance(el, collections.Sequence) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

############################################################
root = make_elem_tree('singapore.osm')
nodes_dict = parse_nodes(root)
nodes_dict = parse_ways(root, nodes_dict)
nodes_dict = parse_relations(root, nodes_dict)
lat_lon_lst = []
description_lst = []
split_dict(lat_lon_lst, description_lst, nodes_dict)
n_items = take(10, nodes_dict.items())

# while True:
#     try:
#         print(n_items)
#         break
#     except:
#         print(x.encode('utf-8') for x in n_items)
#         break
#print(lat_lon_lst[:10])
#print(description_lst[:10])
#print(len(lat_lon_lst)) #991853 nodes
#print(len(description_lst)) #991853 nodes

kdtree = make_kdtree(lat_lon_lst)
save_as_pickle(kdtree, "lat_long_kdtree.pickle")
save_as_pickle(description_lst, "descriptions_list.pickle")

