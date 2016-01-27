#!/usr/bin/env python2.7
# encoding: utf-8

# abremaud@esciencefactory.com 20160107
# code repurposed from http://stackoverflow.com/questions/9924988/python-sparql-quering-a-local-file

import rdflib
import math
from rdflib import Graph

g = Graph()
g.parse('PatchClampSetup_MergedGraphs.nt', format='nt')

query = """
SELECT ?ooo
WHERE {
    {
        ?p <http://www.w3.org/2000/01/rdf-schema#label> ?o .
        ?s ?p ?oo .
        ?s <http://www.w3.org/2000/01/rdf-schema#label> ?ooo .
            FILTER regex(?o, "connected to", "i")
    }
UNION
    {
        ?p <http://www.w3.org/2000/01/rdf-schema#label> ?o .
        ?s ?p ?oo .
        ?oo <http://www.w3.org/2000/01/rdf-schema#label> ?ooo .
            FILTER regex(?o, "connected to", "i")
    }
}
"""


#Process query results
device_list = []
cocount = []
max_len = 0
for row in g.query(query):
    if row[0] in device_list:
        cocount[device_list.index(row[0])] += 1
    else:
        device_list.append(row[0])
        cocount.append(1)
        if len(row[0])>max_len: max_len = len(row[0])


query = """
SELECT ?o
WHERE {
    ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o .
    FILTER NOT EXISTS {?ss ?s ?oo}
}
"""

for row in g.query(query):
    if row[0] not in device_list:
        device_list.append(row[0])
        cocount.append(0)
        if len(row[0])>max_len: max_len = len(row[0])


#Display query results
max_len = max(max_len, len("Device name"))
pad_len = int(math.ceil((max_len + 2 + len("Number of connections") - len(" Example patch-clamp setup "))/2))
print "\n" + "-" * pad_len + " Example patch-clamp setup " + "-" * pad_len
print "Device name" + " " * (max_len-len("Device name")+2) + "Number of connections"

for dev in device_list:
    print dev + " " * (max_len-len(dev)+1), cocount[device_list.index(dev)]
print "-" * pad_len + " Example patch-clamp setup " + "-" * pad_len + "\n"


