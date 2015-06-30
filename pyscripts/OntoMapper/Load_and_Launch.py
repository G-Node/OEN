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

from ontmain import *


############################################
#                                          #
#            DEFINE QUERY SCOPE            #
#                                          #
############################################

#define path to file containing list of terms to be queried from ontologies
#file_path='/Users/admin/Documents/Python_Scripts/OntoMapper/test_terms.csv'
file_path = '/Users/Asus/Documents/GitHub/OEN/'

#define path to file containing list of ontologies, endpoints, and annotation 
# properties with which to run queries
qscope = openQscopeFile(file_path+'pyscripts/OntoMapper/ontos_and_props.csv', '_')


############################################
#                                          #
#            LOAD LIST OF TERMS            #
#    ESTABLISH RECIPIENT DATA STRUCTURE    #
#                                          #
############################################

test=openCSVFile(file_path+'pyscripts/OntoMapper/test_terms.csv', qscope)


############################################
#                                          #
#             PERFORM QUERIES              #
#                                          #
############################################

test2=getSPARQLResults(test, qscope)


############################################
#                                          #
#              FILL-IN INFOS               #
#                                          #
############################################

test3=[]
test3=storeResults(test, test2)


############################################
#                                          #
#             WRITE TO FILES               #
#                                          #
############################################

print
print "- " * 20
print len(test3), "terms explored within specified ontologies."
dictToCSVfile( test3, "csvdict.csv", False )

dictToMappingDashboardCSV(test3)

MappingSummaryCSV(test3)


print
print "- " * 20

test4={}
test5={}
test6={}
test7={}
test8={}
annotlibl   = 'label'
annotsuffix = '_' + annotlibl
for i in test3.keys():
    
    #not previously ontologised
    hasnoexactmatch=True
    for j in test3[i].keys():
        if j[-len(annotsuffix):]==annotsuffix and len(test3[i][j])>0:
            hasnoexactmatch=False
            break
    if hasnoexactmatch:
        test4[i] = test3[i]
        print i, "  \thas no exact label match within specified ontologies."
        
    #Is or is not an oen term already
    isoenterm=False
    for j in test3[i].keys():
        if j[-len("_id"):]=="_id":
            for k in test3[i][j]:
                if "oen_" in k[0].lower():
                    isoenterm = True
                    break
    if isoenterm:
        test5[i] = test3[i]
    else:
        test6[i] = test3[i]
    
    #Has a single unique ID or multiple IDs
    IDset = set()
    for j in test3[i].keys():
        if j[-len("_id"):]=="_id":
            for k in test3[i][j]:
                IDset.add( k )
    if len(IDset)==1:
        test7[i] = test3[i]
    elif len(IDset)>1:
        test8[i] = test3[i]


print str(len(test4)) + "/" + str(len(test3)), "terms were not previously referenced within specified ontologies."
dictToCSVfile( test4, "neverseenbeforeterms.csv", False)

print
print "- " * 20
print str(len(test5)) + "/" + str(len(test3)), "terms already provided with OEN id."
dictToCSVfile( test5, "not_new_to_oen.csv", False)

print
print "- " * 20
print str(len(test6)) + "/" + str(len(test3)), "terms not already provided with OEN id."
dictToCSVfile( test6, "new_to_oen.csv", False)

print
print "- " * 20
print str(len(test7)) + "/" + str(len(test3)), "terms have a unique ID across specified ontologies."
dictToCSVfile( test7, "unique_ids.csv", False)

print
print "- " * 20
print str(len(test8)) + "/" + str(len(test3)), "terms have mulitple IDs across specified ontologies."
dictToCSVfile( test8, "mulitple_ids.csv", False)



'''
############################################
#                                          #
#          DISPLAY DATA STRUCTURE          #
#                                          #
############################################

for i in test3.keys():
    print i
    for j in test3[i].keys():
        #Display only entries containing at least one item
        if len(test3[i][j])>0:
            print "\t", j
            for k in test3[i][j]:
                print "\t\t", k
'''