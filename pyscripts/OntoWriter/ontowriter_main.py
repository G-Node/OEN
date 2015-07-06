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

2015/04/30 ant1b
modified from

http://www.nikhilgopal.com/owlify-a-python-library-to-generate-rdfowl-code/
December 27, 2012 1 by Nikhil Gopal
OWLify: A Python Library to Generate RDF/OWL Code
Example Code
'''


###########################################
#                                         #
#            IMPORTED MODULES             #
#                                         #
###########################################

import os
from OWLify import OWL as OWLclass
from ontospy.ontospy import *
from pyscripts.OntoWriter.ontowriter_functions import splitTermID, avoidSpecials, upOENids
from pyscripts.OntoWriter.ontowriter_functions import OWLrestart, OENimportedClass, reloadOWL
from pyscripts.OntoWriter.ontowriter_functions import shutOWL, ontoUpdate, findClassIDfromLabel
from pyscripts.OntoWriter.ontowriter_functions import listAlreadyUsedIDs
from pyscripts.OntoMapper.ontomapper_functions import *
from nlx_formatted_csv import *


###########################################
#                                         #
#             MAIN EXECUTION              #
#                                         #
###########################################

os.chdir("C:\Users\Asus\Documents\GitHub\OEN\pyscripts\OntoMapper")

#OWLify class 
out = OWLclass("http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl",\
"oen_term.owl", \
"http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/properties")


'''
CHOOSE A CASE TO DISABLE
CASE1: use default hardcoded OWL file head up to defining first 15 oen classes
CASE2: reuse OWL file head from preexisting oen_term.owl file
'''

###########################################
#                                         #
#                  CASE1                  #
#                                         #
###########################################
out = OWLrestart(out)

###########################################
#                                         #
#                  CASE2                  #
#                                         #
###########################################
#out = reloadOWL(out,"C:\Users\Asus\Documents\Github\OEN\pyscripts\OntoMapper\oen_term.owl")
(out, onto) = ontoUpdate(out, "C:\Users\Asus\Documents\Github\OEN\pyscripts\OntoMapper\oen_term.owl")

'''
###########################################
#                                         #
#                ENABLE TO                #
#  IMPORT OEN TERMS FROM CONCEPT BRANCH   #
#                                         #
###########################################

#manage oen id namespace
oen_id_free = range(10000000)
oen_id_used = [i for j in (range(1000), range(2001,10000000)) for i in j]
#oen_id_used = [i for j in (oen_id_used, listAlreadyUsedIDs(onto, "oen_")) for i in j]
oen_id_used = sorted(list(set( oen_id_used )))
oen_id_free = upOENids(oen_id_free, oen_id_used)

#Load all infos from oen_ConceptBranch.csv
header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/oen_ConceptBranch.csv", ",")
oen_CB = LoadCSVwithHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/oen_ConceptBranch.csv", header, ",")

conv_dict = {"rdfs:label":"Label", \
"rdfs:subClassOf":"SuperCategory", \
"obo:IAO_0000115":"Definition", \
"obo:IAO_0000119":"DefiningCitation", \
"obo:IAO_0000118":"Synonym"}

for term in oen_CB:
    ppty_dict = {}
    if "Id" in term.keys() and type(term["Id"]) is str and term["Id"][:len("oen_")]=="oen_":
        oen_id = -1
        try:
            oen_id = int(term["Id"][len("oen_"):])
        except:
            print "could not identify oen_id for:", term["Id"]
        if oen_id==-1 or oen_id in oen_id_used:
            if oen_id in listAlreadyUsedIDs(onto, "oen_"):
                zeropad = "0"*(int(7) - len(str(oen_id)))
                oen_idz = "oen_" + zeropad + str(oen_id)
                print 'Cannot attribute', term["Id"] ,'to "' + term["Label"] + '",', oen_idz, '\talready attributed.'
                #would use to display pre-existing label, but returns empty list.
                #onto.classRepresentation(str(onto.classFind(oen_idz)))["label"]
            else:
                print "oen_id either pertains to exclusion range or not a straight integer:", term["Id"]
            continue
        else:
            for c in conv_dict.keys():
                if conv_dict[c] in term.keys():
                    str_list = term[ conv_dict[c] ].split(",:Category:")
                    str_list[:] = [str_list[k].replace(":Category:","") for k in range(len(str_list)) if str_list[k]!=""]
                    if len(str_list)>0:
                        ppty_dict[ c ] = [] 
                        for s in str_list:
                            ppty_dict[ c ].append( s )
            if "rdfs:subClassOf" not in ppty_dict.keys() or len(ppty_dict["rdfs:subClassOf"])<1:
                ppty_dict[ "rdfs:subClassOf" ] = ["unclassified term"]
            else:
                (out, onto) = ontoUpdate(out, "C:\Users\Asus\Documents\Github\OEN\pyscripts\OntoMapper\oen_term.owl")
                temp_list = []
                for k in ppty_dict["rdfs:subClassOf"]:
                    if type(k) is str and len(k)>0:
                        id_set = findClassIDfromLabel(onto,k)
                        for each_id in id_set:
                            temp_list.append( each_id )
                ppty_dict[ "rdfs:subClassOf" ] = list(set(temp_list))
            if len(ppty_dict[ "rdfs:subClassOf" ])==0:
                ppty_dict[ "rdfs:subClassOf" ] = ["unclassified term"]
                
            zeropad = "0"*(int(7) - len(str(oen_id)))
            oen_idz = "oen_" + zeropad + str(oen_id)
            out = OENimportedClass(out, oen_idz, ppty_dict)
            oen_id_used.append( oen_id )
            oen_id_free.remove( oen_id )
'''

###########################################
#                                         #
#                ENABLE TO                #
#   IMPORT NEW OEN TERMS FOR DEVICE AND   #
#              METHOD BRANCH              #
#                                         #
###########################################
term_dict = openCSVFile("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/OEN_ABrTerms_v02_AllTermsExceptMappedInOBIorERO.csv")

oen_id_free = range(10000000)
oen_id_used = [i for j in (range(18), range(1000,1999)) for i in j]
#oen_id_used = [i for j in (oen_id_used, listAlreadyUsedIDs(onto, "oen_")) for i in j]
oen_id_used = sorted(list(set( oen_id_used )))
oen_id_free = upOENids(oen_id_free, oen_id_used)

for k in term_dict.keys():
    
        #print k

        while oen_id_free[0] in oen_id_used:
            print "multi-id alert:", oen_id_free[0]
            oen_id_used.append( oen_id_free[0] )
            oen_id_free.remove( oen_id_free[0] )

        zeropad = "0"*(int(7) - len(str(oen_id_free[0])))
        oen_id = "oen_" + zeropad + str(oen_id_free[0])
                        
        if len(findClassIDfromLabel(onto,k))>0:
            print 'Some classes already exist with label "' + k + '", not re-attributing.'
            continue

        ppty_dict={}
        ppty_dict["rdfs:label"] = k
        ppty_dict["rdfs:subClassOf"] = "unclassified term"
        for prov in term_dict[k]["provenance"]:
            if type(prov) is str:                        
                compare_str = prov
            elif type(prov) is tuple:                        
                compare_str = prov[0]
            if "is split from" not in compare_str and "unspecified provenance" not in compare_str:
                if "dc:source" not in ppty_dict.keys(): ppty_dict["dc:source"] = []
                ppty_dict["dc:source"].append( compare_str )
                break
        if "dc:source" in ppty_dict.keys():
            out = OENimportedClass(out, oen_id, ppty_dict)
            oen_id_used.append( oen_id_free[0] )
            oen_id_free.remove( oen_id_free[0] )


###########################################
#                                         #
#  FINAL CLOSE DOWN OF OEN_TERM.OWL FILE  #
#                                         #
###########################################
shutOWL(out)

