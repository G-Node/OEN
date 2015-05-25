# -*- coding: utf-8 -*-
#
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



import csv

from ontmain import *


def ImportHeader(file_path="NeuroLex_Brain_Region_Upload_Template.csv"):
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
                
                csv_file = csv.reader(template_file, dialect='excel', delimiter=';')
                
                for row in csv_file:
                        
                        #List of labels from strictly first row of csv file
                        for ppty in row:
                                        
                                header.append( ppty )
                        
                        break
                                        
	except IOError:
	       
	       pass

	return header


def WriteCSVwithHeader(file_path="csv_with_header.csv", header=[], csvdict={}, rt_header={}):
        '''
        Function for writing csv file intended for import within neurolex space.
        header, ordered list of property labels to be considered.
        csvdict, dictionary of contents for each annotation of each term from 
         a manually constructed OWL file.
        rt_header, dictionary specifying for each neurolex property the csvdict 
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
                        
                        if nort:
                                
                                rt_header[ppty] = ppty
        
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
	       
	       pass




'''

header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/NeuroLex_Brain_Region_Upload_Template.csv")
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


onto = OntoInspector("C:\Users\Asus\Documents\GitHub\OEN\pyscripts\OntoMapper\pizza.owl")



import csv
my_file=open('/Users/Asus/csvdict.csv', 'rb')		
csv_file=csv.reader(my_file, dialect='excel', delimiter=';')
test3 = {}
headerskip = False
for row in csv_file:
    if headerskip:
        if len(row[0])>0: 
            term  = row[0]
            test3[term] = {}
        if len(row[1])>0:
            annot = row[1]
            test3[term][annot] = []
        test3[term][annot].append( row[2] )
    else:
        headerskip = True
WriteCSVwithHeader("csv_with_header.csv", header, test3, rt_header)

'''