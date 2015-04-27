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
			csvdict[row[0]] = {\
			"neurolex_id":'', "neurolex_definition":'', "neurolex_label":'', "neurolex_related":set(), \
			"NEMO_id":''    , "NEMO_definition":''    , "NEMO_label":''    , "NEMO_related":set(),     \
			"OBI_id":''     , "OBI_definition":''     , "OBI_label":''     , "OBI_related":set(),      \
			"ERO_id":''     , "ERO_definition":''     , "ERO_label":''     , "ERO_related":set()       }
	
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
		
			nlx_output=getData(neurolex_endpoint, "", i)
			biop_output=getData(bioportal_endpoint, "NEMO", i)
			onto_output=getData(ontofox_endpoint, "OBI", i)
		
		elif option=="nlx":
	
			nlx_output[i]=getData(neurolex_endpoint, "", i)
			
		elif option=="bio":
		
			biop_output=getData(bioportal_endpoint, "NEMO", i)
			    						
		elif option=="onto":
		
			onto_output=getData(ontofox_endpoint, "OBI", i)
			
		else:
	
			print("You entered a wrong option!")
	
	print("nlx_output est un", type(nlx_output))
	return nlx_output

	
def storeResults(csvdict, nlx_output):
        
        for onto in nlx_output.keys():
            
                onto_output = crossonto_output[onto]
                
                for i in onto_output.keys():

                        labels = []
                        ids    = []
                                            
                        for result in nlx_output["results"]["bindings"]:

                                labels.append(result['label']['value'])
                                ids.append(result['x']['value'])
        
#                        #Check number of label and id corresponding to the key
#                        if labels.count(i)>1:
#                  
#                                csvdict[i]["neurolex_id"]=
     			
        return csvdict
