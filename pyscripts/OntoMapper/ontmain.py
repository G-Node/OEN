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



from ontomapper import *
import csv
import copy
import difflib

def openQscopeFile(file_path,option=""):
        """
	Function to extract from csv file containing ontologies to be queried from,
	corresponding endpoints and properties to be sought
        """
        
        Qscope = {}
        
        try:
                
                scope_file = open(file_path,'rb')
                
                csv_file = csv.reader(scope_file, dialect='excel', delimiter=';')
                
                for row in csv_file:
                        
                        if row[0] not in Qscope.keys():
                                
                                Qscope[row[0]] = []
                                
                        for item in row[1:]:
                                
                                if len(item)>0:
                                
                                        Qscope[row[0]].append( item )

                #identify full urls for those properties self-referenced within each ontology
                if "ontology" in Qscope.keys():
                        
                        #keep ontologies whose name contains charstr "option"
                        if type(option) is str and len(option)>2:
                            
                                for onto_param in ["endpoint", "prefixes", "from_uri"]:
                                        
                                        if onto_param in Qscope.keys():
                                                
                                                Qscope[onto_param][:] = [Qscope[onto_param][Qscope["ontology"].index(tup)] \
                                                for tup in Qscope["ontology"] if option in tup]
                                        
                                Qscope["ontology"][:] = [tup for tup in Qscope["ontology"] if option in tup]
                        

                        #Duplicate of Qscope, truncated for querying only the labels
                        # and ids of annotation properties of interest from each ontology
                        qscope_noopt = {}                        
                        for k in Qscope.keys():
                                if k != "optional": 
                                        qscope_noopt[k] = Qscope[k]
                        
                        
                        for onto in Qscope["ontology"]:
                        
                                for putativ_annot in Qscope["optional"]:
                                    
                                    newdata = getData( qscope_noopt, onto, putativ_annot )
                                    
                                    for result in newdata["results"]["bindings"]:
                                        
                                            if "label" in result.keys() and "value" in result['label'] and result['label']['value'].lower()==putativ_annot.lower():
        
                                                    if "noprefix" not in Qscope.keys():
                                                            
                                                            Qscope["noprefix"] = {}
                                                            
                                                    Qscope["noprefix"][result['label']['value']] = result['id']['value']

	except IOError:
		pass

	scope_file.close()
	
	return Qscope
	

def openCSVFile(file_path,qscope):
	""" 
	Function to open the csv file and extract the data from the file as key of a 			
	dictionary that will store the different mapping results
	"""
	csvdict={}	
	
	try:

                #Establish template for individual entries
                ontostruct = {}
                
                for k in qscope["ontology"]:
                        
                        for kk in qscope["mandatory"]:
                            
                                ontostruct[ k + "_" + kk ] = []
                
                        for kkk in qscope["optional"]:
                                
                                ontostruct[ k + "_" + kkk ] = set()
                
                #Create templated entries for each term listed in file	       
		my_file=open(file_path, 'rb')
		
		csv_file=csv.reader(my_file, dialect='excel')
		
		for row in csv_file:
			
			csvdict[row[0]]=copy.deepcopy(ontostruct)
			
			decomp = row[0].lower()
			
			csvdict[row[0]]["provenance"] = []
			
			if len(row)>1: csvdict[row[0]]["provenance"].append(row[1])
			
			for hyph in ['-','_']:
			    
			         decomp = decomp.replace(hyph," ")
			 
			decomp = decomp.split()
			
			if len(decomp)>1:
			    
			         for subterm in decomp:
			                 
			                 if type(subterm) is str and len(subterm)>2:
			             
			                         if subterm not in csvdict.keys():
			         
    			                                 csvdict[subterm]=copy.deepcopy(ontostruct)
    			                                 csvdict[subterm]["provenance"] = []
    			                 
    			                         csvdict[subterm]["provenance"].append("is split of: " + row[0])

	except IOError:

		pass

	my_file.close()
	
	return csvdict

						
def getSPARQLResults(csvdict, qscope, option=""):
        
        crossonto_output = {}
        
        for onto_ind, onto in enumerate(qscope["ontology"]):
                
                if onto not in crossonto_output.keys():
                        
                        crossonto_output[ onto ] = {}
	
                for i in csvdict.keys():
                                        
                        try:
                                crossonto_output[onto][i] = getData( qscope, onto, i )
                        except:
                                pass
	
	return crossonto_output
	
#	print("nlx_output est un", type(nlx_output))
#	return nlx_output
	
def storeResults(csvdict, crossonto_output):
        
        for onto in crossonto_output.keys():
            
                onto_output = crossonto_output[onto]

                for i in onto_output.keys():
                        
                        lpoi = {}
                        
                        #ListPropertiesOfInterest as Rosetta Stone between query result keys and original property names
                        for o in csvdict[i].keys():
                                
                                if onto+"_" in o and len(onto)<len(o):
                                        
                                        lpoi[formatAsRDFSpropertyLabel(o[len(onto)+1:])] = o[len(onto)+1:]
                        
                        #For each query match obtained
                        for result in onto_output[i]["results"]["bindings"]:
                                
                                #Store values of all properties returned by query when label matches exactly the sought term
                                if 'label' in result.keys() and 'value' in result['label'] and result['label']['value'].lower()==i.lower():
                                        
                                        #For each property matched within the query match
                                        for res in result.keys():
                                                
                                                if 'value' in result[res]:
                                                        
                                                        if res in lpoi.keys():
                                                                
                                                                #Mandatory fields, intended to be "label" and "id"
                                                                if type(csvdict[i][onto+"_"+lpoi[res]]) is list:
                                                                        
                                                                        csvdict[i][onto+"_"+lpoi[res]].append( result[res]['value'] )
                                                                
                                                                #Other fields, customisable via onto_and_props.csv file
                                                                elif type(csvdict[i][onto+"_"+lpoi[res]])is set:
                                                                        
                                                                        csvdict[i][onto+"_"+lpoi[res]].add( result[res]['value'] )
                                                                        
                                                        else:
                                                                
                                                                print res, "not in", lpoi.keys()
                                                                
                                                else:
                                                        
                                                        pass
                                
                                #Store label returned within query as "related entry" in case match to sought term is not exact
                                else:
                                        
                                        if "related" in lpoi.keys() and "label" in result.keys() and "id" in result.keys():
                                                
                                                if "value" in result["label"] and "value" in result["id"]:
                                                        
                                                        if type(csvdict[i][onto+"_"+lpoi["related"]]) is list:
                                                                
                                                                csvdict[i][onto+"_"+lpoi["related"]].append( result["label"]['value'] )
                                                                
                                                        elif type(csvdict[i][onto+"_"+lpoi["related"]])is set:
                                                                
                                                                csvdict[i][onto+"_"+lpoi["related"]].add( result["label"]['value'] )
                                                                
                                        else:
                                            
                                                print "query item not stored as related to: ", i.lower()
     	
        return csvdict


def dictToCSVfile(csvdict,file_path="csvdict.csv",verbose=False):
    
    print "Writing dictionary down."

    with open(file_path, 'wb') as csvfile:
            
            fieldnames = ['term', 'property', 'content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=';')    
            writer.writeheader()

            # terms
            for k in csvdict.keys():
                    
                    newp = True
                    
                    # Establish annotations writing order
                    match_score = {}
                    
                    for p in csvdict[k].keys():
                        
                            for q in csvdict[k].keys():
                                    
                                    a = p
                                    b = q
                                            
                                    if '_' in a: a = a[a.index('_')+1:]
                                    if '_' in b: b = b[b.index('_')+1:]
                                            
                                    if a in match_score.keys():
                                            match_score[a] += difflib.SequenceMatcher(None, a, b).ratio()
                                    else:
                                            match_score[a]  = difflib.SequenceMatcher(None, a, b).ratio()
                            
                    match_score = sorted(match_score, key=match_score.get, reverse=True)
                            
                    # Write down in established order
                    monitorlist = []
                                        
                    for w in match_score:
                            
                            for p in csvdict[k].keys():
                                    
                                    a = p
                                    if '_' in a: a = a[a.index('_')+1:]
                                    
                                    if w==a:
                                            
                                            monitorlist.append( p )
                                            newi = True

                                            for i in csvdict[k][p]:
                                            
                                                    if newp and newi:
                                                            
                                                            writer.writerow({'term': k, 'property': p, 'content': i})
                                                            if verbose: print "> ", k, "\t", p, "\t", i
                                                            newp = False
                                                            newi = False
                                                    
                                                    elif newi:
                                                    
                                                            writer.writerow({'property': p, 'content': i})
                                                            if verbose: print "> " + " "*len(k) + "\t", p, "\t", i
                                                            newi = False
                                                            
                                                    else:
                                                            
                                                            writer.writerow({'content': i})
                                                            if verbose: print "> " + " "*len(k) + "\t" + " "*len(p) + "\t", i

                    #Consistency checks
                    for w in monitorlist:
                            if monitorlist.count(w)>1:
                                    print " !!! ", w, "  repeated annotation, term =", k, "  !!! "
                            if w not in csvdict[k].keys():
                                    print " !!! ", w, "  de novo annotation, term =", k, "  !!! "
                    for p in csvdict[k].keys():
                            if p not in monitorlist:
                                    print " !!! ", p, "  annotation was dropped, term =", k, "  !!! "

    print "Dictionary finished writing down."



#                        for result in nlx_output["results"]["bindings"]:
#        
#                            labels.append(result['label']['value'])
#                            ids.append(result['x']['value'])
        
#                        #Check number of label and id corresponding to the key
#                        if labels.count(i)>1:
#                  
#                                csvdict[i]["neurolex_id"]=ids