#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.cElementTree as ET
import pprint
import re

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Ave." : "Avenue",
            "Rd" : "Road",
            "Rd." : "Road",
            }

def count_tags(filename):
    # YOUR CODE HERE
    tags = {}
    for event,elem in ET.iterparse(filename):
        if not elem.tag in tags:
            tags[elem.tag] = 1
        else:
            tags[elem.tag] = tags[elem.tag] + 1
    return tags

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        k = element.attrib["k"]
        if re.match(lower, k):
            keys["lower"] += 1
        elif re.match(lower_colon, k):
            keys["lower_colon"] += 1
        elif re.search(problemchars, k):
            print "problemchars",k
            keys["problemchars"] += 1
        else:
            print "other",k
            keys["other"] += 1
    return keys

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def print_tag_key_names(filename):
    for event,elem in ET.iterparse(filename):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if 1:  # check street name
                    if tag.attrib['k'] == "addr:street":
                        print elem.tag, "addr:street", tag.attrib['v']
                    if tag.attrib['k'] == "name:en":
                        print elem.tag, "name:en", tag.attrib['v']
                if 1:  # check city, districy, province
                    if  tag.attrib['k'] == "addr:city":
                        print elem.tag, "addr:city", tag.attrib['v']
                    if  tag.attrib['k'] == "addr:district":
                        print elem.tag, "addr:district", tag.attrib['v']
                    if  tag.attrib['k'] == "addr:province":
                        print elem.tag, "addr:province", tag.attrib['v']
                if 1:  # check postCode
                    if  tag.attrib['k'] == "addr:postcode":
                        print elem.tag, "addr:postcode", tag.attrib['v']
def test(filename):
    ### check tages
    tags = count_tags(filename)
    print("tags")
    pprint.pprint(tags)

    ### check tags k
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    print("\ntag - ks")
    pprint.pprint(keys)

    ### check tag key name
    print("")
    print_tag_key_names(filename)

if __name__ == "__main__":
    filename = 'data_sample/ex_shanghai_sample.osm'
    #filename = 'data/ex_shanghai.osm'
    test(filename)