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



##########################################
#                                        #
#            IMPORTED MODULES            #
#                                        #
##########################################

import csv

from ontmain import *


###########################################
#                                         #
#            SUPPORT FUNCTIONS            #
#                                         #
###########################################

def ImportHeader(file_path="oen_ConceptBranch.csv", option=";"):
        '''        
        Function for retrieving a list of property labels from the first row of 
         a csv file.
        
        Intent is for the list to provide the basis for the header of another 
         csv file, which will subsequently be populated with corresponding 
         content from a manually constructed OWL file. 
        
        Final csv file should allow for import within neurolex space.
        '''
        
        header = []
        
        try:
                
                template_file = open(file_path, 'rb')
                
                csv_file = csv.reader(template_file, dialect='excel', delimiter=option)
                
                for row in csv_file:
                        
                        #List of labels from strictly first row of csv file
                        for ppty in row:
                                        
                                header.append( ppty )
                        
                        break
                                        
	except IOError:
	       
	       pass

	return header


def LoadCSVwithHeader(file_path="oen_ConceptBranch.csv", header=[], option=";"):
        
        oen_CB = []

        filename = file_path
        if "/" in file_path:
                filename = filename[::-1]
                filename = filename[:filename.index("/")]
                filename = filename[::-1]
        
        print " Loading according to header from csv file:", filename
                        
        try:
        
                my_file=open(file_path, 'rb')
      		
       	        csv_file=csv.reader(my_file, dialect='excel', delimiter=option)
       	
       	        headerskip = False
      		
       	        for row in csv_file:
        	       
        	       if headerskip == True:
        	               
        	               oen_CB.append({})
        	               
        	               N = len(oen_CB)-1
        	               
        	               for k in range(max(len(row),len(header))):
        	                       
        	                       if k<len(row) and k<len(header):
        	                               
        	                               if header[k] != "":
        	                       
        	                                       oen_CB[N][ header[k] ] = row[ k ]
        	                                       
        	                               else:
        	                                       
        	                                       oen_CB[N][ "header_" + "0"*(int(len(str(len(row)))-len(str(k)))) + str(k) ] = row[ k ]
        	                               
        	                       if k<len(row) and k>=len(header):
        	                               
        	                               oen_CB[N][ "header_" + "0"*(int(len(str(len(row)))-len(str(k)))) + str(k) ] = row[ k ]
        	                               
        	                       if k>=len(row) and k<len(header):
        	                               
        	                               break
        
        	       else:
        	               
        	               headerskip = True
	  
        except:
                
                print "Could not load according to header from csv file:",  filename
                pass
	  
        return oen_CB



def WriteCSVwithHeader(file_path="csv_with_header.csv", header=[], csvdict={}, rt_header={}):
        '''
        Function for writing csv file intended for import within neurolex space.
        
        header: ordered list of property labels to be considered.
        
        csvdict: dictionary of contents for each annotation of each term from 
         a manually constructed OWL file.
        
        rt_header: dictionary specifying for each neurolex property the csvdict 
         contained annotation label the content of which can be used to populate
         the file.
        '''

        try:
                
                #autospecify reverse-transcripts for unspecified properties
                for ppty in header:
                        
                        nort = True
                        
                        for rt_ppty in rt_header.keys():
                                
                                if rt_ppty.lower() == ppty.lower():
                                        
                                        nort = False
                                        break
                        
                        if nort: rt_header[ppty] = ppty
                
                with open(file_path, 'wb') as csvfile:
                    
                        fieldnames = header
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=';')    
                        writer.writeheader()

                        for k in csvdict.keys():
                                
                                rowdict = {}
                                
                                for ppty in header:
                                        
                                        if ppty not in rowdict:
                                                                                
                                                #rowdict[ppty] = []
                                                rowdict[ppty] = "'"
                                        
                                        for candid in rt_header.keys():
                                                
                                                if ppty.lower() == candid.lower():
                                                        
                                                        for dk in csvdict[k].keys():
                                                                
                                                                if  dk.lower() == rt_header[candid].lower():
                                                                        
                                                                        if type(csvdict[k][dk]) is not list:
                                                                                
                                                                                if rowdict[ppty]=="'":
                                                                                        
                                                                                        rowdict[ppty] = csvdict[k][dk]
                                                                                
                                                                                else:
                                                                                        
                                                                                        rowdict[ppty] += "\n"+csvdict[k][dk]
                                                                        
                                                                        else:
                                                                                
                                                                                for j in csvdict[k][dk]:
                                                                                        
                                                                                        #rowdict[ppty].append(j)
                                                                                        if rowdict[ppty]=="'":
                                                                                                
                                                                                                rowdict[ppty] = j
                                                                                        
                                                                                        else:
                                                                                                
                                                                                                rowdict[ppty] += "\n"+j
                                
                                writer.writerow( rowdict )

	except IOError:
	       
	       print "EXECUTION WAS NOT SUCCESFUL"
	       pass



'''
########################################################
#                                                      #
#            EXECUTION SNIPPETS FOR TESTING            #
#                                                      #
########################################################

header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/NeuroLex_oen_ConceptBranch_Template.csv")
rt_header = {}
for ppty in header:
    if ppty.lower() not in rt_header.keys():
        rt_header[ ppty.lower() ] = "ERO_"+ppty.lower()
rt_header[ "RelatedTo" ] = "ERO_related"


#file_path = '/Users/Asus/Documents/GitHub/OEN/'
#qscope    = openQscopeFile(file_path+'pyscripts/OntoMapper/ontos_and_props.csv', 'ERO')
#test      = openCSVFile(file_path+'pyscripts/OntoMapper/test_terms.csv', qscope)
#test2     = getSPARQLResults(test, qscope)
#test3     = []
#test3     = storeResults(test, test2)

#for i in test3.keys():
#    print i
#    for j in test3[i].keys():
#        #Display only entries containing at least one item
#        if len(test3[i][j])>0:
#            print "\t", j
#            for k in test3[i][j]:
#                print "\t\t", k

#WriteCSVwithHeader("csv_with_header.csv", header, test3, rt_header)


header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/NeuroLex_oen_ConceptBranch_Template.csv")


#patch-up provenance field contents
#fill-in initial provenance info for split-up terms
for i in test3.keys():
    if "provenance" in test3[i].keys():
        for k, j in enumerate(test3[i]["provenance"]):
            if type(j) is tuple and len(j)>0:
                j = j[0]
                if "is split of: " in j and " from [" not in j:
                    orig_label = j[len("is split of: "):]
                    if orig_label in test3.keys() and len(test3[orig_label]["provenance"])>0 \
                    and type(test3[orig_label]["provenance"][0]) and len(test3[orig_label]["provenance"][0])>0:                    
                        test3[i]["provenance"][k] = ("is split from [" + test3[orig_label]["provenance"][0][0] + "]: " + orig_label, "", "")
                        print j, " => ", test3[i]["provenance"][k]


WriteCSVwithHeader("csv_with_header.csv", header, test3)
'''

