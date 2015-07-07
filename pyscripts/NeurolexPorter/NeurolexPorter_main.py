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



###########################################
#                                         #
#            IMPORTED MODULES             #
#                                         #
###########################################

import os, inspect
from ontospy.ontospy import *
from neurolexporter_functions import labelListFromPropertyID, ImportHeader
from neurolexporter_functions import LoadCSVwithHeader, WriteCSVwithHeader

filename   = inspect.getframeinfo(inspect.currentframe()).filename
scriptpath = os.path.dirname(os.path.abspath(filename))
oenpath    = scriptpath[:scriptpath.find('OEN\\')+4]

os.chdir( oenpath )

from pyscripts.generic_functions.generic_functions import splitTermID


###########################################
#                                         #
#             MAIN EXECUTION              #
#                                         #
###########################################

csvdict = {}

onto = Ontology( oenpath+"pyscripts\data\NeurolexPorter_data\NeurolexPorter_input\oen_term.owl" )

header = ImportHeader( oenpath+"pyscripts\data\NeurolexPorter_data\NeurolexPorter_input\oen_ConceptBranch.csv", ",")

fw_header = {}
for h in header:
    if h not in fw_header.keys():
        fw_header[h] = h
    else:
        if type(fw_header[h]) is not list:
            fw_header[h] = [ h ]
        else:
            fw_header[h].append( h )
fw_header["SuperCategory"]    = "subClassOf"
fw_header["DefiningCitation"] = "definition source"
fw_header["RelatedTo"]        = "alternative term"

for clas in onto.allclasses:
        
        print
        print "- "*12
        
        label_list = []
        #unwrapStruct( onto.classRepresentation(clas) )
        #print
        
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
                        
                        temp = onto.classRepresentation(clas)["class"]
                        temp = temp[::-1]
                        temp = temp[:temp.index("/")]
                        temp = temp[::-1]
                                
                        csvdict[ onto.classRepresentation(clas)["class"] ]["id"].append( temp )
                        
                        if "label" in onto.classRepresentation(clas).keys():
                                
                                if "label" not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["label"] = []
                                        
                                if type( onto.classRepresentation(clas)["label"] ) is str:
                                    
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["label"].append( onto.classRepresentation(clas)["label"] )
                                        print temp, " ", onto.classRepresentation(clas)["label"]
                                        
                                elif type( onto.classRepresentation(clas)["label"] ) is list and len(  onto.classRepresentation(clas)["label"] )>0:
                                        
                                        csvdict[ onto.classRepresentation(clas)["class"] ]["label"].append( onto.classRepresentation(clas)["label"][0] )
                                        print temp, " ", onto.classRepresentation(clas)["label"][0]
                                        
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
                                                        
                                                        #print "*", h, "\t", fw_header[h], "\t", tripl[0]
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
                                                                        
                                                                        #print "**", h, "\t", fw_header[h].lower(), "\t", tripl[0], "i.e.", afuri.lower()
                                                                        
                                                                        if h not in csvdict[ onto.classRepresentation(clas)["class"] ].keys():
                                                                                
                                                                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ] = []
                                                                                
                                                                        if tripl[1] not in csvdict[ onto.classRepresentation(clas)["class"] ][ h ]:
                                                                                
                                                                                csvdict[ onto.classRepresentation(clas)["class"] ][ h ].append( tripl[1] )
                                                                                
                                #print
                else:
                        
                        print "multiple occurences of class:", onto.classRepresentation(clas)["class"]
                        
        else:
                
                print "class without an id:", clas

WriteCSVwithHeader(oenpath+"pyscripts\data\NeurolexPorter_data\NeurolexPorter_output\\"+\
                    "oen_DeviceAndMethodBranch.csv", header, csvdict)