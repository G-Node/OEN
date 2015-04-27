from ontomapper import *
import csv
import copy

def openQscopeFile(file_path):
        """
	Function to extract from csv file containing ontologies to be queried,
	corresponding endpoints and properties to be sought
        """
        
        Qscope = {}
        
        try:
                
                scope_file = open(file_path,'rb')
                
                csv_file = csv.reader(scope_file, dialect='excel', delimiter=';')
                
                for row in csv_file:
                        
                        if row[0] not in Qscope.keys():
                                
                                Qscope[row[0]] = set()
                                
                        for item in row[1:]:
                                
                                if len(item)>0:
                                
                                        Qscope[row[0]].add( item )
        
	except IOError:
		pass

	scope_file.close()
	
	return Qscope
	

def openCSVFile(file_path):
	""" 
	Function to open the csv file and extract the data from the file as key of a 			
	dictionary that will store the different mapping results
	"""
	csvdict={}
	
	try:
	       
		my_file=open(file_path, 'rb')
		
		csv_file=csv.reader(my_file, dialect='excel')
		
		ontostruct = {\
		"neurolex_id":[], "neurolex_definition":[], "neurolex_label":[], "neurolex_related":set(), \
		"NEMO_id":[]    , "NEMO_definition":[]    , "NEMO_label":[]    , "NEMO_related":set(),     \
		"OBI_id":[]     , "OBI_definition":[]     , "OBI_label":[]     , "OBI_related":set(),      \
		"ERO_id":[]     , "ERO_definition":[]     , "ERO_label":[]     , "ERO_related":set()       }
		
		for row in csv_file:
			
			csvdict[row[0]]=copy.deepcopy(ontostruct)
			
			decomp = row[0].lower()
			
			for hyph in ['-','_']:
			    
			         decomp = decomp.replace(hyph," ")
			 
			decomp = decomp.split()
			
			if len(decomp)>1:
			    
			         for subterm in decomp:
			             
			                 if subterm not in csvdict.keys():
			         
    			                         csvdict[subterm]=copy.deepcopy(ontostruct)
				
	except IOError:
		pass
	my_file.close()
	
	return csvdict

						
def getSPARQLResults(csvdict, option):

	nlx_output    = {}
	biop_output   = {}
	onto_output   = {}
	eaglei_output = {}
	
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
			try:
			    eaglei_output[i]=getData(ontofox_endpoint, "ERO", i)
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
		
		elif option=="eaglei":
		      
		      try:
		          eaglei_output[i]=getData(ontofox_endpoint, "ERO", i)
		      except:
		          pass
		
		else:
	
			print("You entered a wrong option!")
	
	return {"NLX":nlx_output,"OBI":onto_output,"NEMO":biop_output,"ERO":eaglei_output}
	
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
                        
                elif onto == "ERO":

                        uri_trunk  = "http://purl.obolibrary.org/obo/ERO_"
                        labelstr   = "ERO_label"
                        idstr      = "ERO_id"
                        relatedstr = "ERO_related"
                        
                else:
                        
                        print "Cross-ontology query not familiar"
                        onto_output = {}
                                        

                for i in onto_output.keys():
                        
                        labels = []
                        ids    = []                        
                    
                        for result in onto_output[i]["results"]["bindings"]:
                                
                                labels.append(result['label']['value'])
                                ids.append(   result[  'x'  ]['value'])
                        
                        for heidi, label in enumerate(labels):
                                
                                if label.lower() == i.lower():
                                        
                                        csvdict[i][labelstr].append(   label    )
                                        csvdict[i][ idstr  ].append( ids[heidi] )
                                            
                                else:
                                                                        
                                        csvdict[i][relatedstr].add( ids[heidi] )
     	
        return csvdict

#                        for result in nlx_output["results"]["bindings"]:
#        
#                            labels.append(result['label']['value'])
#                            ids.append(result['x']['value'])
        
#                        #Check number of label and id corresponding to the key
#                        if labels.count(i)>1:
#                  
#                                csvdict[i]["neurolex_id"]=ids