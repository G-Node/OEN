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



############################################
#                                          #
#             IMPORTED MODULES             #
#                                          #
############################################

import os, inspect
from ontomapper_functions import openQscopeFile, openCSVFile, getSPARQLResults
from ontomapper_functions import storeResults, dictToCSVfile, dictToMappingDashboardCSV
from ontomapper_functions import dictToMappingSummaryCSV


filename   = inspect.getframeinfo(inspect.currentframe()).filename
scriptpath = os.path.dirname(os.path.abspath(filename))
if "OEN\\" in scriptpath:
    oenpath    = scriptpath[:scriptpath.find('OEN\\')+4]
else:
    oenpath = scriptpath + "\\"

OMS  = 'pyscripts/data/OntoMapper_data/OntoMapper_input/ontology_metadata_schema.csv'
LOT  = 'pyscripts/data/OntoMapper_data/OntoMapper_input/list_of_terms.csv'


############################################
#                                          #
#            DEFINE QUERY SCOPE            #
#                                          #
############################################

qscope = openQscopeFile( oenpath+OMS, '_' )


############################################
#                                          #
#            LOAD LIST OF TERMS            #
#    ESTABLISH RECIPIENT DATA STRUCTURE    #
#                                          #
############################################

csvdict_empty = openCSVFile( oenpath+LOT , qscope )


############################################
#                                          #
#             PERFORM QUERIES              #
#                                          #
############################################

qres_struct = getSPARQLResults( csvdict_empty, qscope )


############################################
#                                          #
#              FILL-IN INFOS               #
#                                          #
############################################

csvdict_filled = storeResults( csvdict_empty, qres_struct )


############################################
#                                          #
#             WRITE TO FILES               #
#                                          #
############################################

dictToCSVfile( csvdict_filled, oenpath+"pyscripts/data/OntoMapper_data/OntoMapper_output/csvdict.csv", False )

dictToMappingDashboardCSV( csvdict_filled, oenpath+"pyscripts/data/OntoMapper_data/OntoMapper_output/MappingDashboard.csv" )

dictToMappingSummaryCSV( csvdict_filled, oenpath+"pyscripts/data/OntoMapper_data/OntoMapper_output/MappingSummary.csv" )

