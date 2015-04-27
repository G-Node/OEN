from ontmain import *

#define path to file containing list of terms to be queried from ontologies
file_path='/Users/admin/Documents/Python_Scripts/OntoMapper/test_terms.csv'
file_path='/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/test_terms.csv'

#define path to file containing list of ontologies, endpoints, and annotation properties with which to run queries
qscope = openQscopeFile('/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/ontos_and_props.csv', "OBI")

print qscope

test=openCSVFile(file_path, qscope)

test2=getSPARQLResults(test, qscope)

test3=[]

test3=storeResults(test, test2)

for i in test3.keys():
    print i
    for j in test3[i].keys():
        print "\t", j
        for k in test3[i][j]:
            print "\t\t", k
