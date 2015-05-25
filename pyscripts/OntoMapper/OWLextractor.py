# -*- coding: utf-8 -*-
################################################################################
#
# Work on Ontology for Experimental Neurophysiology (c) by <ylefranc> and <ant1b>
#
# This work is licensed under a
# Creative Commons Attribution 4.0 International License.
#
# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by/4.0/>.
#
################################################################################



'''
13/05/2015, ant1b contrib
modified from
http://www.michelepasin.org/blog/2011/07/18/inspecting-an-ontology-with-rdflib/
#"Inspecting an ontology using RDFLib"

Functions for loading the contents of an ontology described in a OWL file.
Functions for retrieving specific contents

uses python package ontospy
    which requires python library rdflib
'''


from ontospy.ontospy import *
from nlx_formatted_csv import *


def labelListFromPropertyURI( onto, prop_id ):
    label_list = []
    prop_id = prop_id.replace(":","/")
    for p in onto.allproperties:
        if prop_id in p:
            if "alltriples" in onto.propertyRepresentation( p ).keys():
                for k in onto.propertyRepresentation( p )["alltriples"]:
                    if "rdfs:label" in k[0]:
                        label_list.append( k[1] )
    return label_list

def unwrapStruct( struct, depth=0 ):
    if type(struct) is tuple:
        for j in struct:
            unwrapStruct( j, depth )
    elif type(struct) is list:
        depth += 1
        for k in struct:
            unwrapStruct( k, depth )
        depth -= 1
    elif type(struct) is dict:
        depth += 1
        for k in struct.keys():
            unwrapStruct( (k, struct[k]), depth )
        depth -= 1
    else:
        print " "*depth, struct
        
    

csvdict = {}

#onto = Ontology("C:\Users\Asus\Documents\GitHub\OEN\pyscripts\OntoMapper\pizza.owl")
onto = Ontology("C:\Users\Asus\Documents\Travail\OEN\uids_fromERO.owl")

header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/NeuroLex_Brain_Region_Upload_Template.csv")

fw_header = {}
for h in header:
    if h not in fw_header.keys():
        fw_header[h] = h
    else:
        if type(fw_header) is not list:
            fw_header[h] = [ h ]
        fw_header[h].append( h )
fw_header["SuperCategory"] = "subClassOf"
fw_header["DefiningCitation"] = "citation"
fw_header["RelatedTo"] = "synonym"

for clas in onto.allclasses:
    label_list = []
    #unwrapStruct( onto.classRepresentation(clas) )
    if "class" in onto.classRepresentation(clas).keys():
        if onto.classRepresentation(clas)["class"] not in csvdict.keys():
            csvdict[ onto.classRepresentation(clas)["class"] ] = {}
            if "id" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                csvdict[ onto.classRepresentation(clas)["class"] ]["id"] = []
            csvdict[ onto.classRepresentation(clas)["class"] ]["id"].append( onto.classRepresentation(clas)["class"] )
            if "label" in onto.classRepresentation(clas).keys():
                if "label" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                    csvdict[ onto.classRepresentation(clas)["class"] ]["label"] = []
                if type( onto.classRepresentation(clas)["label"] ) is str:
                    csvdict[ onto.classRepresentation(clas)["class"] ]["label"].append( onto.classRepresentation(clas)["label"] ) 
                elif type( onto.classRepresentation(clas)["label"] ) is list and len( onto.classRepresentation(clas)["label"] )>0:
                    csvdict[ onto.classRepresentation(clas)["class"] ]["label"].append( onto.classRepresentation(clas)["label"][0] )
            if "comment" in onto.classRepresentation(clas).keys():
                if "comment" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                    csvdict[ onto.classRepresentation(clas)["class"] ]["comment"] = []
                if type( onto.classRepresentation(clas)["comment"] ) is str:
                    csvdict[ onto.classRepresentation(clas)["class"] ]["comment"].append( onto.classRepresentation(clas)["comment"] )
                elif type( onto.classRepresentation(clas)["comment"] ) is list and len( onto.classRepresentation(clas)["comment"] )>0:
                    csvdict[ onto.classRepresentation(clas)["class"] ]["comment"].append( onto.classRepresentation(clas)["comment"][0] )
            if "alltriples" in onto.classRepresentation(clas).keys():
                for tripl in onto.classRepresentation(clas)["alltriples"]:
                    for h in fw_header.keys():
                        #print "*", h, "\t", fw_header[h], "\t", tripl[0], " ", len( labelListFromPropertyURI( onto, tripl[0] ) )
                        if fw_header[h] in tripl[0] and h:
                            print "*", h, "\t", fw_header[h], "\t", tripl[0]
                            if h not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ] = []
                            if tripl[1] not in csvdict[ onto.classRepresentation(clas)["class"] ][ h ]:
                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ].append( tripl[1] )                            
                        elif len( labelListFromPropertyURI( onto, tripl[0] ) )>0:
                            #print "**", h, "\t", fw_header[h], "\t", len( labelListFromPropertyURI( onto, tripl[0] ) )
                            for afuri in labelListFromPropertyURI( onto, tripl[0] ):                                
                                if fw_header[h].lower() in afuri:
                                    print "**", h, "\t", fw_header[h], "\t", afuri
                                    if afuri not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                        csvdict[ onto.classRepresentation(clas)["class"] ][ afuri ] = []
                                    if tripl[1] not in csvdict[ onto.classRepresentation(clas)["class"] ][ afuri ]:
                                        csvdict[ onto.classRepresentation(clas)["class"] ][ afuri ].append( tripl[1] )
                #print
        else:
            print "multiple occurences of class:", onto.classRepresentation(clas)["class"]
    else:
        print "class without an id:", clas

WriteCSVwithHeader("csv_with_header.csv", header, csvdict)