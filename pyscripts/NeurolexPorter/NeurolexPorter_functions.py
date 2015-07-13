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


###########################################
#                                         #
#            SUPPORT FUNCTIONS            #
#                                         #
###########################################


def labelListFromPropertyID( onto, prop_id ):
    '''
    onto: OntoSPy ontology structure
    
    prop_id: annotation property short identifier e.g. obo:IAO_0000115
    
    label_list: list of annotation property labels corresponding to uris 
     matching prop_id within onto
    '''
    label_list = []
    prop_id = prop_id.replace(":","/")
    for p in onto.allproperties:
        if prop_id in p:
            if "alltriples" in onto.propertyRepresentation( p ).keys():
                for k in onto.propertyRepresentation( p )["alltriples"]:
                    if "rdfs:label" in k[0]:
                        label_list.append( k[1] )
    return label_list


def unwrapStruct( struct, depth=0 ):
    if type(struct) is tuple:
        for j in struct:
            unwrapStruct( j, depth )
    elif type(struct) is list:
        depth += 1
        for k in struct:
            unwrapStruct( k, depth )
        depth -= 1
    elif type(struct) is dict:
        depth += 1
        for k in struct.keys():
            unwrapStruct( (k, struct[k]), depth )
        depth -= 1
    else:
        print " "*depth, struct


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

