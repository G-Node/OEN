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



from ontmain import *

#define path to file containing list of terms to be queried from ontologies
file_path='/Users/admin/Documents/Python_Scripts/OntoMapper/test_terms.csv'
file_path='/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/test_terms.csv'

#define path to file containing list of ontologies, endpoints, and annotation properties with which to run queries
qscope = openQscopeFile('/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/ontos_and_props.csv')

print qscope

test=openCSVFile(file_path, qscope)

test2=getSPARQLResults(test, qscope)

test3=[]

test3=storeResults(test, test2)

for i in test3.keys():
    print i
    for j in test3[i].keys():
        #Display only entries containing at least one item
        if len(test3[i][j])>0:
            print "\t", j
            for k in test3[i][j]:
                print "\t\t", k
