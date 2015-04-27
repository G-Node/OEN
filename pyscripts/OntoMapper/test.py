from ontmain import *

file_path='/Users/admin/Documents/Python_Scripts/OntoMapper/test_terms.csv'
file_path='/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/test_terms.csv'

test=openCSVFile(file_path)

test2=getSPARQLResults(test, "nlx")

for k in test2.keys():
    print k
    if "results" in test2[k]:
        if "bindings" in test2[k]["results"]:
            for kk in test2[k]["results"]["bindings"]:
                if "label" in kk.keys() and "value" in kk["label"]:
                    print "\t", kk["label"]["value"]
                if "x" in kk.keys() and "value" in kk["x"]:
                    print "\t", kk["x"]["value"]
