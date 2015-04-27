from ontomapper import *
import csv

def openCSVFile(file_path):
	""" 
	Function to open the csv file and extract the data from the file as key of a 			
	dictionary that will store the different mapping results
	"""
	csvdict={}
	
	try:
		my_file=open(file_path, 'rb') 
		csv_file=csv.reader(my_file, dialect='excel')
		for row in csv_file:
			print("Just before")
			ontostruct = {\
			"neurolex_id":'', "neurolex_definition":'', "neurolex_label":'', "neurolex_related":set(), \
			"NEMO_id":''    , "NEMO_definition":''    , "NEMO_label":''    , "NEMO_related":set(),     \
			"OBI_id":''     , "OBI_definition":''     , "OBI_label":''     , "OBI_related":set(),      \
			"ERO_id":''     , "ERO_definition":''     , "ERO_label":''     , "ERO_related":set()       }
			
			csvdict[row[0]]=ontostruct
			
			decomp = row[0].lower()
			for hyph in ['-','_']:
			         decomp = decomp.replace(hyph," ")
			decomp = decomp.split()
			if len(decomp)>1:
			         for subterm in decomp:
			                 if subterm not in csvdict.keys():
			         
    			                         csvdict[subterm]=ontostruct
				
	except IOError:
		pass
	my_file.close()
	
	return csvdict
						
def getSPARQLResults(csvdict, option):

	nlx_output ={}
	biop_output={}
	onto_output={}
	
	for i in csvdict.keys():
	
		if option=="all":
		
			try:
			    nlx_output[i] =getData(neurolex_endpoint, "", i)
 			except:
 			    pass
 			try:
 			    biop_output[i]=getData(bioportal_endpoint, "NEMO", i)
			except:
			    pass
			try:
			    onto_output[i]=getData(ontofox_endpoint, "OBI", i)
			except:
			    pass
		
		elif option=="nlx":
	
			try:
			    nlx_output[i] =getData(neurolex_endpoint, "", i)
			except:
			    pass
			
		elif option=="bio":
		
			try:
			    biop_output[i]=getData(bioportal_endpoint, "NEMO", i)
			except:
			    pass			     
			    						
		elif option=="onto":
		
			try:
			    onto_output[i]=getData(ontofox_endpoint, "OBI", i)
			except:
			    pass
			
		else:
	
			print("You entered a wrong option!")
	
	return {"NLX":nlx_output,"OBI":onto_output,"NEMO":biop_output}
	
#	print("nlx_output est un", type(nlx_output))
#	return nlx_output
	
def storeResults(csvdict, crossonto_output):
        
        for onto in crossonto_output.keys():
            
                onto_output = crossonto_output[onto]
                
                if onto == "NLX":
                        
                        uri_trunk  = "http://neurolex.org/wiki/Nlx_"
                        labelstr   = "neurolex_label"
                        idstr      = "neurolex_id"
                        relatedstr = "neurolex_related"
                        
                elif onto == "OBI":
                        
                        uri_trunk  = "http://purl.obolibrary.org/obo/OBI_"
                        labelstr   = "OBI_label"
                        idstr      = "OBI_id"
                        relatedstr = "OBI_related"                        
                
                elif onto == "NEMO":

                        uri_trunk  = "http://purl.bioontology.org/NEMO/ontology/NEMO.owl#NEMO_"
                        labelstr   = "NEMO_label"
                        idstr      = "NEMO_id"
                        relatedstr = "NEMO_related"

                else:
                        
                        print "Cross-ontology query not familiar"
                        onto_output = {}
                                        

                for i in onto_output.keys():
                        
                        labels = []
                        ids    = []
                    
                        for result in onto_output[i]["results"]["bindings"]:
                                
                                labels.append(result['label']['value'])
                                ids.append(   result[  'x'  ]['value'])
                                            
#                    for result in nlx_output["results"]["bindings"]:
#        
#                        labels.append(result['label']['value'])
#                        ids.append(result['x']['value'])

                        labels_set = set(labels)
        
                        for label in labels_set:
                                
                                k=0
                                conflict_ids = []
                                
                                while labels[k:].count(label)>0:
                                        
                                        k = labels.index(label,k)
                                        
                                        #Collect reference numbers of uris with identical label
                                        
                                        if uri_trunk in ids[k]:
                                                
                                                conflict_ids.append( ids[k][len(uri_trunk):] )
                                                
                                        k += 1
                                
                                #Keep the uri with the smallest reference number in case of doublon
                                
                                if len(conflict_ids)>1:
                                        
                                        try:
                                                
                                                smallest = int(filter(type(conflict_ids[0]).isdigit, conflict_ids[0]))
                                                
                                                smal_ind = 0
                                                
                                                for eye in conflict_ids:
                                                        
                                                        if smallest>int(filter(type(eye).isdigit, eye)):
                                                                
                                                                smallest = int(filter(type(eye).isdigit, eye))
                                                                
                                                                smal_ind = conflict_ids.index(eye)
                                        
                                                heidi = ids[ ids.index(uri_trunk + conflict_ids[smal_ind]) ]
                                                
                                        except:
                                                
                                                print "ID conflict unresolved"
                                                heidi = ids[ k-1 ]
                                
                                else:
                                        
                                        heidi = ids[ k-1 ]
        
                                if i.upper() == label.upper():
        
                                        csvdict[i][labelstr] = label
                                        csvdict[i][ idstr  ] = heidi
                                        
                                else:
                                        
                                        csvdict[i][relatedstr].add( heidi )
        
#                        #Check number of label and id corresponding to the key
#                        if labels.count(i)>1:
#                  
#                                csvdict[i]["neurolex_id"]=ids
     			
        return csvdict
