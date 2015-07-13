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

import os, sys, inspect, shutil
from OWLify import OWL as OWLclass
from ontospy.ontospy import *
from ontowriter_functions import upOENids, OENimportedClass
from ontowriter_functions import reloadOWL, shutOWL, ontoUpdate
from ontowriter_functions import findClassIDfromLabel, listAlreadyUsedIDs

filename   = inspect.getframeinfo(inspect.currentframe()).filename
scriptpath = os.path.dirname(os.path.abspath(filename))
if "pyscripts" in scriptpath:
    oenpath = scriptpath[:scriptpath.lower().find('pyscripts')]
else:
    oenpath = scriptpath + "\\"

os.chdir( oenpath )
sys.path.append( oenpath + "pyscripts" )

from generic_functions.generic_functions import splitTermID, avoidSpecials
from OntoMapper.ontomapper_functions import openCSVFile


###########################################
#                                         #
#             MAIN EXECUTION              #
#                                         #
###########################################

os.chdir( oenpath+"pyscripts\data\OntoWriter_data\OntoWriter_output" )

#OWLify class 
out = OWLclass("http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl",\
                "oen_term.owl", \
                "http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/properties")

shutil.copy( oenpath+"pyscripts\data\OntoWriter_data\OntoWriter_input\oen_term.owl", \
                oenpath+"pyscripts\data\OntoWriter_data\OntoWriter_output")

out = reloadOWL(out, oenpath+"pyscripts\data\OntoWriter_data\OntoWriter_output\oen_term.owl" )
(out, onto) = ontoUpdate(out, oenpath+"pyscripts\data\OntoWriter_data\OntoWriter_output\oen_term.owl" )



###########################################
#                                         #
#   IMPORT NEW OEN TERMS FOR DEVICE AND   #
#              METHOD BRANCH              #
#                                         #
###########################################
term_dict = openCSVFile( oenpath+"pyscripts\data\OntoWriter_data\OntoWriter_input\unmapped_terms.csv")

oen_id_free = range(10000000)
oen_id_used = [i for j in (range(18), range(1000,1999)) for i in j]
oen_id_used = [i for j in (oen_id_used, listAlreadyUsedIDs(onto, "oen_")) for i in j]
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

