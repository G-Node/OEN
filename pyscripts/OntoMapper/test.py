from ontmain import *

file_path='/Users/admin/Documents/Python_Scripts/OntoMapper/test_terms.csv'
file_path='/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/test_terms.csv'

qscope = openQscopeFile('/Users/Asus/Dropbox/OEN_INCF_WorkDocument/Mapping_Python/OntoMapper/ontos_and_props.csv')

test=openCSVFile(file_path)

test2=getSPARQLResults(test, "onto")

test3=[]

test3=storeResults(test, test2)

#for i in test3.keys():
#    print i
#    for j in test3[i].keys():
#        print "\t", j
#        for k in test3[i][j]:
#            print "\t\t", k

#Display "csvdict" data structure contents:
for i in test3.keys():
    #csvdict key
    print i
    if test3[i]["neurolex_label"]!=[] or test3[i]["neurolex_id"]!=[]:        
        #Label & onto-ID
        for k, j in enumerate(test3[i]["neurolex_label"]):            
            print "\t", j, "\t", test3[i]["neurolex_id"][k]            
    if len(test3[i]["neurolex_related"])>0:        
        #Related entries onto-IDs
        for j in test3[i]["neurolex_related"]:            
            print "\tNLX\t", j
        print
    if test3[i]["OBI_label"]!=[] or test3[i]["OBI_id"]!=[]:
        for k, j in enumerate(test3[i]["OBI_label"]):
            print "\t", j, "\t", test3[i]["OBI_id"][k]
    if len(test3[i]["OBI_related"])>0:
        for j in test3[i]["OBI_related"]:
            print "\tOBI\t", j
        print
    if test3[i]["NEMO_label"]!=[] or test3[i]["NEMO_id"]!=[]:
        for k, j in enumerate(test3[i]["NEMO_label"]):
            print "\t", j, "\t", test3[i]["NEMO_id"][k]
    if len(test3[i]["NEMO_related"])>0:
        for j in test3[i]["NEMO_related"]:
            print "\tNEMO\t", j
        print
    if test3[i]["ERO_label"]!=[] or test3[i]["ERO_id"]!=[]:
        for k, j in enumerate(test3[i]["ERO_label"]):
            print "\t", j, "\t", test3[i]["ERO_id"][k]
    if len(test3[i]["ERO_related"])>0:
        for j in test3[i]["ERO_related"]:
            print "\tERO\t", j
        print
