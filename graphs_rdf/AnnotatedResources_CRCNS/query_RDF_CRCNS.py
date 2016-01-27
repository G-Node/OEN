#!/usr/bin/env python2.7
# encoding: utf-8

# abremaud@esciencefactory.com 20160107
# code repurposed from http://stackoverflow.com/questions/9924988/python-sparql-quering-a-local-file

import sys
import rdflib
import math
from rdflib import Graph


def pad_for_centering(c_w, str):
    str = " "*int((c_w-len(str))/2) + str + " "*((c_w-len(str))-int((c_w-len(str))/2))
    return str


def dataset_isabout_query( keyw ):

    try:

        full_rdf = ""
        for f in ['CRCNS_pvc-9_AnnotationGraph.nt',\
                  'CRCNS_hc3_AnnotationGraph.nt',\
                  'CRCNS_ret1_AnnotationGraph.nt']:
            file_string = open( f, "rU")
            full_rdf = full_rdf + file_string.read() + "\n"
            file_string.close()

        g = Graph()
        g.parse( data=full_rdf, format='nt')


        query = """
        SELECT DISTINCT ?s ?oo
        WHERE {
                ?s ?p ?o .
                ?o <http://www.w3.org/2000/01/rdf-schema#label> ?oo .
                    FILTER regex(?oo, "%s", "i")
        }
        ORDER BY ?s
        """ %str(keyw)

        #print len(g.query(query))

        print "\nDatasets about '" + str(keyw) + "':"
        c1_w,c2_w = 0,0
        for row in g.query(query):
            if c1_w < len(row[0]): c1_w = len(row[0])
            if c2_w < len(row[1]): c2_w = len(row[1])
        header = pad_for_centering(c1_w, "Dataset CRCNS url") + \
              "\t| " + \
              pad_for_centering(c2_w, "OEN class label")
        print header
        print "-" * (len(header)+2)
        for row in g.query(query):
            print row[0], "\t| " + row[1]
        print "\n"

    except:
        print "Something went wrong with the querying..."


if __name__ == '__main__':
    OK = False
    if sys.argv[1:]:
        
        try:
            dataset_isabout_query( str(sys.argv[1]) )
            OK = True
        except:
            print "\nCould not use argument provided as a string."
            pass

    if not OK:
        print "Please provide some string we can query against."
        print "\nHere is a default example of output using 'microscop' as input,"
        print "\tdataset_isabout_query('microscop')\n"
        dataset_isabout_query( str('microscop') )
    
