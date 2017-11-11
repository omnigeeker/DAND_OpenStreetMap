#!/usr/bin/env python
#-*- coding: UTF-8 -*- 
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from pymongo import MongoClient

"""
{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "201203",
          "street": "肇家浜路"
          "street:en": "Zhao Jia Bang Road"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "星巴克咖啡",
"name:en"："StarBucks Coffee"
"phone": "1 (773)-271-5176"
}
"""

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

roi_infos = set(["amenity","cuisine","phone","name"])

# UPDATE THIS VARIABLE
mapping = { "St": "Street", "St.": "Street",
            "Ave" : "Avenue", "Ave." : "Avenue",
            "Rd" : "Road", "Rd." : "Road",
            "Hwy" : "Highway", "Hwy." : "Highway",
            }

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def is_cn_street_name(k):
    return (k == "addr:street")

def is_en_street_name(k):
    return (k == "addr:street:en")

def is_postcode(k):
    return (k == "addr:postcode")

def audit_cn_street_name(v):
    index_lu = v.find(u"路")
    if index_lu == -1:
        return v
    elif index_lu == len(v)-1:
        return v
    else:
        print "audit_cn_street_name ", v, v[:index_lu+1]
        return v[:index_lu+1]
    return v

def audit_en_street_name(v):
    items = v.split(" ")
    changed = False
    for i in range(len(items)):    
        if mapping.has_key(items[i]):
            changed = True
            items[i] = mapping[items[i]]
    v = " ".join(items)
    if changed: print "audit_en_street_name", v
    return v

def check_postcode(v):
    if len(v) != 6:
        return False
    if v[0]!='2' or v[1]!='0':
        return False
    for i in range(2,6):
        if not v[i].isdigit():
            return False
    return True

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node["id"] = element.attrib["id"]
        node["type"] = element.tag
        if element.attrib.has_key("visible"):
            node["visible"] = element.attrib["visible"]
        node["created"]= {}
        node["address"]= {}
        for k in CREATED:
            if element.attrib.has_key(k):
                node["created"][k] = element.attrib[k]
        if element.attrib.has_key("lat") and element.attrib.has_key("lon"):
            node["pos"] = [float(element.attrib["lat"]), 
                           float(element.attrib["lon"])]
        for tag in element.iter("tag"):
            k = tag.attrib["k"]
            v = tag.attrib["v"]
            ## 处理中文路名
            if is_cn_street_name(k):
                node["address"]["steet"] = audit_cn_street_name(v)
            ## 处理英文路名
            if is_en_street_name(k):
                node["address"]["steet:en"] = audit_en_street_name(v)
            ## 处理邮编
            if is_postcode(k):
                if check_postcode(v):
                    node["address"]["postcode"] = v
                else:
                    print "no a valid postcode: ",v
            ## 处理英文名称
            if k == "name:en":
                node["name:en"] = audit_en_street_name(v)
            ## 处理其他
            if k in roi_infos:
                node["k"] = v

        if element.tag == "way":
            for nd in element.iter("nd"):
                if not node.has_key("node_refs"):
                    node["node_refs"] = []
                node["node_refs"].append(nd.attrib["ref"])
        return node
    else:
        return None


def test_process_map(file_in):
    # You do not need to change this file
    data = []
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            data.append(el)
    return data

def test(filename):
    data = test_process_map(filename)
    pprint.pprint(data[:10])

def save_to_mongodb(filename):
    client = MongoClient("mongodb://localhost:27017")
    db = client.openstreetmap
    print "begin insert all data into mongodb openstreetmap"
    i = 0
    for _, element in ET.iterparse(filename):
        el = shape_element(element)
        if el:
            #insert to mongo db
            db.arachnid.insert(el)
            i += 1
            if i % 2000 == 0:
                print "insert %d data"%i
    print("total insert %d data"%i)
    print ""
    print "end insert all data into mongodb openstreetmap"
    print db.arachnid.find_one()                

if __name__ == "__main__":
    # filename = 'data_sample/ex_shanghai_sample.osm'
    # test(filename)
    
    filename = 'data/ex_shanghai.osm'
    save_to_mongodb(filename)