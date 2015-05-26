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
###########################################
#                                         #
#            GENERAL COMMENTS             #
#                                         #
###########################################

13/05/2015, ant1b contrib
modified from
http://www.michelepasin.org/blog/2011/07/18/inspecting-an-ontology-with-rdflib/
#"Inspecting an ontology using RDFLib"
25/05/2015, may not have much to do with above cited reference anymore.

Functions for loading the contents of an ontology described in a OWL file.
Functions for retrieving specific contents

uses python package OntoSPy
    which requires python library rdflib
'''

###########################################
#                                         #
#            IMPORTED MODULES             #
#                                         #
###########################################

from ontospy.ontospy import *
from nlx_formatted_csv import *


###########################################
#                                         #
#            SUPPORT FUNCTIONS            #
#                                         #
###########################################

def labelListFromPropertyID( onto, prop_id ):
    '''
    onto: OntoSPy ontology structure
    
    prop_id: annotation property short identifier e.g. obo:IAO_0000115
    
    label_list: list of annotation property labels corresponding to uris 
     matching prop_id within onto
    '''
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
        

###########################################
#                                         #
#             MAIN EXECUTION              #
#                                         #
###########################################

csvdict = {}

#onto = Ontology("C:\Users\Asus\Documents\GitHub\OEN\pyscripts\OntoMapper\pizza.owl")
#onto = Ontology("C:\Users\Asus\Documents\Travail\OEN\uids_fromERO.owl")
onto = Ontology("C:\Users\Asus\Documents\Travail\OEN\inclAllChild_fromERO.owl")

header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/NeuroLex_Brain_Region_Upload_Template.csv")

fw_header = {}
for h in header:
    if h not in fw_header.keys():
        fw_header[h] = h
    else:
        if type(fw_header[h]) is not list:
            fw_header[h] = [ h ]
        else:
            fw_header[h].append( h )
fw_header["SuperCategory"] = "subClassOf"
fw_header["DefiningCitation"] = "definition source"
fw_header["RelatedTo"] = "alternative term"

for clas in onto.allclasses:
        
        label_list = []
        #unwrapStruct( onto.classRepresentation(clas) )        
        
        #Class representation includes a "class" field?
        if "class" in onto.classRepresentation(clas).keys():
                
                #Content of "class" field (i.e. class uri) not already a csvdict key.
                if onto.classRepresentation(clas)["class"] not in csvdict.keys():

                        '''
                        Create csvdict entry for class uri
                        Create sub-entries to csvdict "class uri" entry: id, label, comment,
                         fill-in with class representation fields direct content.
                        '''

                        csvdict[ onto.classRepresentation(clas)["class"] ] = {}
                        
                        if "id" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                
                                csvdict[ onto.classRepresentation(clas)["class"] ]["id"] = []
                                
                        csvdict[ onto.classRepresentation(clas)["class"] ]["id"].append( onto.classRepresentation(clas)["class"] )
                        
                        if "label" in onto.classRepresentation(clas).keys():
                                
                                if "label" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["label"] = []
                                        
                                if type( onto.classRepresentation(clas)["label"] ) is str:
                                    
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["label"].append( onto.classRepresentation(clas)["label"] ) 
                                        
                                elif type( onto.classRepresentation(clas)["label"] ) is list and len(  onto.classRepresentation(clas)["label"] )>0:
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["label"].append( onto.classRepresentation(clas)["label"][0] )
                                        
                        if "comment" in onto.classRepresentation(clas).keys():
                                
                                if "comment" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["comment"] = []
                                        
                                if type( onto.classRepresentation(clas)["comment"] ) is str:
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["comment"].append( onto.classRepresentation(clas)["comment"] )
                                        
                                elif type( onto.classRepresentation(clas)["comment"] ) is list and len(  onto.classRepresentation(clas)["comment"] )>0:
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["comment"].append( onto.classRepresentation(clas)["comment"][0] )
                        
                        '''
                        Create custom sub-entries to csvdict "class uri" entry:
                         fill-in with contents from class representation field
                         "alltriples".
                        '''
                        
                        if "alltriples" in onto.classRepresentation(clas).keys():
                                
                                for tripl in onto.classRepresentation(clas)["alltriples"]:
                                        
                                        for h in fw_header.keys():
                                                
                                                #print "*", h, "\t", fw_header[h], "\t", tripl[0], " ", len( labelListFromPropertyID( onto, tripl[0] ) )
                                                
                                                #case annotation label explicitly stated as first element of triples                                                
                                                if fw_header[h] in tripl[0]:
                                                        
                                                        print "*", h, "\t", fw_header[h], "\t", tripl[0]
                                                        if h not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                                                
                                                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ] = []
                                                        
                                                        if tripl[1] not in csvdict[ onto.classRepresentation(clas)["class"] ][ h ]:
                                                                
                                                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ].append( tripl[1] )
                                                                
                                                #case annotation id is stated instead of annotation label
                                                elif len( labelListFromPropertyID( onto, tripl[0] ) )>0:
                                                        
                                                        #print "**", h, "\t", fw_header[h], "\t", len( labelListFromPropertyID( onto, tripl[0] ) )
                                                        
                                                        #browse through annotation labels corresponding to stated annotation id
                                                        for afuri in labelListFromPropertyID( onto, tripl[0] ):
                                                                
                                                                if fw_header[h].lower() == afuri.lower()[1:-1]:
                                                                        
                                                                        print "**", h, "\t", fw_header[h].lower(), "\t", tripl[0], "i.e.", afuri.lower()
                                                                        
                                                                        if h not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                                                                
                                                                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ] = []
                                                                                
                                                                        if tripl[1] not in csvdict[ onto.classRepresentation(clas)["class"] ][ h ]:
                                                                                
                                                                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ].append( tripl[1] )
                                                                                
                                #print
                else:
                        
                        print "multiple occurences of class:", onto.classRepresentation(clas)["class"]
                        
        else:
                
                print "class without an id:", clas

WriteCSVwithHeader("csv_with_header.csv", header, csvdict)