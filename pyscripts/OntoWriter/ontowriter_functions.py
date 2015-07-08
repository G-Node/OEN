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

import os, sys, inspect
from OWLify import OWL as OWLclass
from ontospy.ontospy import *


filename   = inspect.getframeinfo(inspect.currentframe()).filename
scriptpath = os.path.dirname(os.path.abspath(filename))
if "pyscripts" in scriptpath:
    oenpath = scriptpath[:scriptpath.lower().find('pyscripts')]
else:
    oenpath = scriptpath + "\\"

os.chdir( oenpath )
sys.path.append( oenpath + "pyscripts" )

from generic_functions.generic_functions import splitTermID, avoidSpecials


###########################################
#                                         #
#           SUPPORT FUNCTIONS             #
#                                         #
###########################################


def OENimportedClass(OWL, oen_id, ppty_dict):
    '''
    Function to add a class entry by appending required text to the doc field of 
     an owlify owl object. 
    
    OWL: instance of the owlify OWL class.
    
    oen_id: string constituted of prefix "oen_" and reference integer to be 
     attributed to the new class left padded with zeros up to seven characters,
     for a standard grand total of 11 characters.
    
    ppty_dict: dictionary with annotation properties to be included within class 
     declaration as keys, and corresponding expected content as values.
     e.g. {"obo:IAO_0000115":"A thing that is not another one", etc.}
    '''
    
    stub = '\n    <!-- ' + OWL.namespace + '/' + oen_id + ' -->\n'
    stub += '\n    <owl:Class rdf:about="&oen_term;' + oen_id + '">\n'
    for prefix in ppty_dict.keys():
        if type(ppty_dict[prefix]) is str: ppty_dict[prefix] = [ ppty_dict[prefix] ]
        if type(ppty_dict[prefix]) is list:
            for ppty in ppty_dict[prefix]:
                if type(ppty) is not str: ppty = str(ppty)
                if prefix=="rdfs:subClassOf" and ppty.lower() in ["oen_0000000", "unclassified term"]:
                    stub += '    \t<rdfs:subClassOf rdf:resource="&oen_term;oen_0000000"/>\n'
                elif prefix=="rdfs:subClassOf" and ppty[:len("oen_term:oen_")].lower() == "oen_term:oen_":
                    temp = -1
                    try:
                        temp = int( ppty[len("oen_term:oen_"):] )
                    except:
                        print "Encountered non integer value of oen id"
                        pass
                    if temp in range(10000000):
                        zeropad = "0"*(int(7) - len(str(temp)))
                        oen_idz = "oen_" + zeropad + str(temp)
                        stub += '    \t<' + prefix + ' rdf:resource="&oen_term;' + oen_idz + '"/>\n'
                    else:
                        stub += '    \t<' + prefix + ' xml:lang="en">' + avoidSpecials(ppty) + '</' + prefix + '>\n'
                else:
                    stub += '    \t<' + prefix + ' xml:lang="en">' + avoidSpecials(ppty) + '</' + prefix + '>\n'
    stub += '    </owl:Class>\n\n\n'
    print stub
    OWL.doc += stub
    return OWL


def reloadOWL(OWL,file_path="oen_term.owl"):
    '''
    Function to make the doc field of an owlify owl object the exact replica of 
     the body of a pre-existing owl file.
    
    OWL: instance of the owlify OWL class.
    
    file_path: the path to the owl file to be reloaded.
    
    '''
    filename = file_path
    if "/" in file_path:
        filename = filename[::-1]
        filename = filename[:filename.index("/")]
        filename = filename[::-1]
    try:
        with open(file_path, "r") as myfile:
            data=myfile.read()
        if "</rdf:RDF>" in data:
            fromtheend = len(data) - data.index("</rdf:RDF>")
            OWL.doc = data[:-fromtheend]
        else:
            print "Could not reload OWL from:", filename
    except:
        print "Could not reload OWL from:", filename
    return OWL


def shutOWL(OWL):
    '''
    Function to tie down doc field of an owlify owl object and write it to disk
     using the filenam specified in its outfile field.
    
    OWL: instance of the owlify owl class.
    
    '''
    filename = OWL.outfile
    if "/" in OWL.outfile:
        filename = filename[::-1]
        filename = filename[:filename.index("/")]
        filename = filename[::-1]
    try:        
        fileh = open(OWL.outfile, 'w')
        OWL.doc += '</rdf:RDF>\n'        
        fileh.write(OWL.doc)
        fileh.close()
    except:
        print "Could not shut OWL:", filename


def ontoUpdate(OWL, file_path="oen_term.owl"):
    '''
    Function to return matching OntoSPy ontology object and owlify owl object, 
     based using a pre-existing owl file as reference.
    
    OWL: instance of the owlify owl class.
        
    file_path: path to the owl file used as reference.
    
    onto: instance of the OntoSPy ontology class.
        
    '''
    
    
    filename = file_path
    if "/" in file_path:
        filename = filename[::-1]
        filename = filename[:filename.index("/")]
        filename = filename[::-1]
    try:    
        shutOWL(OWL)
        onto = Ontology(file_path)
        OWL = reloadOWL(OWL)
    except:
        print "could not update ontology:", filename
        onto = []
    return OWL, onto


def findClassIDfromLabel(onto,k):
    '''
    Function to return the set of class identifiers of all classes for which a
     rdfs:label annotation can be found that matches the spelling of the 
     provided string, within an OntoSPy ontology object.
    
    onto: instance of the OntoSPy ontology class.
        
    k: string to be matched.
    
    id_set: set of OntoSPy ontology classname identifiers.
    
    '''
    
    id_set = set()
    for clas in onto.allclasses:
        if "alltriples" in onto.classRepresentation(clas).keys():
            for tripl in onto.classRepresentation(clas)["alltriples"]:
                if tripl[0] == "rdfs:label" and tripl[1][1:-1].lower() == k.lower():
                    try:
                        id_set.add( str( onto.classRepresentation(clas)["classname"] ) )
                    except:
                        print "Class ID could not be retrieved:", onto.classRepresentation(clas)["classname"]
    return id_set


def listAlreadyUsedIDs( onto, option="" ):
    '''
    Function to return a list of the identifiers of all existing classes within
     an OntoSPy ontology object.
    
    onto: instance of the OntoSPy ontology class.
        
    option: string that can be used to specify a classname to be fully or 
     partially matched as fetching criteria.
    
    id_list: list of OntoSPy ontology classname identifiers.
    
    '''
    # classFind expected format: 
    # [rdflib.term.URIRef(u'http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000000')]
    #e.g. use as option: "oen_"
    id_list = []
    try:
        if option=="":
            for clas in onto.allclasses:
                id_list.append( onto.classRepresentation(clas)["classname"] )
        else:
            id_list = onto.classFind( option )
        id_list[:] = [int(splitTermID( str(k) )[1]) for k in id_list]
        id_list = sorted(list(set(id_list)))
    except:
        print "Could not use OntoSPy classFind()"
    return id_list


def upOENids(oen_id_free,oen_id_used):
    '''
    Function to obtain remove from a list of integers those that pertain to 
     another list.
    
    oen_id_free: list of integers that correspond to non-allocated identifiers.
    
    oen_id_used: list of integers that correspond to allocated identifiers.
    
    '''
    oen_id_free = set(oen_id_free) - set(oen_id_used)
    return sorted(list(oen_id_free))
      


'''
###########################################
#                                         #
#   IMPORT OEN TERMS FROM CONCEPT BRANCH  #
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

