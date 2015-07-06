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
import copy
import difflib
from SPARQLWrapper import SPARQLWrapper, JSON

from pyscripts.generic_functions.generic_functions import formatAsRDFSpropertyLabel, Tuplify_LblIdDef, encodeForWriting


###########################################
#                                         #
#             MAJOR FUNCTIONS             #
#                                         #
###########################################

def openQscopeFile(file_path,option=""):
        '''
	Function to extract from csv file containing ontologies to be queried 
	 from, the corresponding endpoints, prefixes and uris, as well as the 
	 labels of annotations to be sought (field: "optional").
	
	option: string for restricting selected ontologies to those specified in
	 the csv file whose name also contains the exact same sequence of (>2) 
	 characters.
	
	Qscope: dict reporting ontologies queried from (field: "ontology"), 
	 endpoints to be used (field: "endpoint"), prefixes (field: "prefixes"), 
	 uris (field: "from_uri"), and custom list of annotation labels to be 
	 queried (field: "optional") and their ontology specific uri (field: "noprefix").
        '''
                                
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

                #identify full urls for those annotations self-referenced within each ontology
                if "ontology" in Qscope.keys():
                        
                        #keep ontologies whose name contains charstr "option"
                        if type(option) is str and len(option)>2:
                            
                                for onto_param in ["endpoint", "prefixes", "from_uri"]:
                                        
                                        if onto_param in Qscope.keys():
                                                
                                                Qscope[onto_param][:] = [Qscope[onto_param][Qscope["ontology"].index(tup)] \
                                                for tup in Qscope["ontology"] if option in tup]
                                        
                                Qscope["ontology"][:] = [tup for tup in Qscope["ontology"] if option in tup]
                        
                        
                        for onto in Qscope["ontology"]:
                                
                                #Duplicate of Qscope, truncated for querying only the labels
                                # and ids of annotation properties of interest from each ontology
                                qscope_noopt = {}
                                onto_ind = Qscope["ontology"].index( onto )
                                for k in Qscope.keys():
                                        if k in ["ontology","endpoint","prefixes","from_uri"]:
                                                qscope_noopt[k] = []
                                                qscope_noopt[k].append( Qscope[k][onto_ind] )
                                        elif k not in ["optional","noprefix"]:
                                                qscope_noopt[k] = Qscope[k]
                        
                                for putativ_annot in Qscope["optional"]:

                                        newdata = getData( qscope_noopt, onto, putativ_annot )
                                    
                                        for result in newdata["results"]["bindings"]:
                                        
                                                if "label" in result.keys() and "value" in result['label'] and result['label']['value'].lower()==putativ_annot.lower():
        
                                                        if "noprefix" not in Qscope.keys():
                                                            
                                                                Qscope["noprefix"] = {}
                                                                
                                                        if onto not in Qscope["noprefix"].keys():
                                                                
                                                                Qscope["noprefix"][onto] = set()
                                                            
                                                        Qscope["noprefix"][onto].add( (result['label']['value'], result['id']['value']) )

	except IOError:
		pass

	scope_file.close()
	
	return Qscope
	

def openCSVFile(file_path,qscope={"ontology":"","endpoint":"","prefixes":"","from_uri":""}):
	'''
	Function to open the csv file and extract the data from the file as key 
	 of a dictionary that will store the different mapping results according
	 to the template specified in qscope.
	
	csv file:
	    column1; column2
	    term   ; provenance
	
	Tip: during extraction, the subparts of terms that happen to be 
	 compounds become terms in their own right as direct primary key to
	 csvdict data structure.
	
	Qscope: dict reporting ontologies queried from (field: "ontology"), 
	 endpoints to be used (field: "endpoint"), prefixes (field: "prefixes"), 
	 uris (field: "from_uri"), and custom list of annotation labels to be 
	 queried (field: "optional") and their ontology specific uri (field: 
	 "noprefix").
	
	csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key. Tip1: requires a correctly formatted qscope data 
	 structure (see below). Tip2: generate fully formed qscope structure 
	 using openQscopeFile function.
	'''
	
	##e.g.
        #Qscope = {"ontology":[],"endpoint":[],"prefixes":[],"from_uri":[]}
        ##fields with one content per ontology, 1:1:1:1 and order matters
        #Qscope["ontology"].append("NEMO")
        #Qscope["endpoint"].append("http://sparql.bioontology.org/sparql")
        #Qscope["prefixes"].append("""
        # prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        # prefix owl: <http://www.w3.org/2002/07/owl#>
        # prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        # """)
        #Qscope["from_uri"].append("http://bioportal.bioontology.org/ontologies/")
        ##fields specifying unordered list of annotation labels
        #Qscope["mandatory"].append( "label" )
        #Qscope["mandatory"].append( "id" )
        #Qscope["optional"].append( "related" )
        #Qscope["optional"].append( "definition source" )
        #Qscope["optional"].append( "pref_term" )
        ##etc.
        ##see "annotations" sections of ontology of interest for label spellings
	
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
		
		csv_file=csv.reader(my_file, dialect='excel', delimiter=';')
		
		for row in csv_file:
		      
		      if type(row[0]) is str and len(row[0])>0:
		              
		              if row[0] not in csvdict.keys():
		                      
		                      csvdict[row[0]]=copy.deepcopy(ontostruct)
		                      csvdict[row[0]]["provenance"] = []
		              
		              decomp = row[0].lower()
		              
		              if len(row)>1: 
		                      
		                      csvdict[row[0]]["provenance"].append(row[1])
		              
		              else:
		                      
		                      csvdict[row[0]]["provenance"].append("unspecified provenance")		                      
		              
		              for hyph in ['-','_']:
		                      
		                      decomp = decomp.replace(hyph," ")
		              
		              decomp = decomp.split()
		              
		              if len(decomp)>1:
		                      
		                      for subterm in decomp:
		                              
		                              if type(subterm) is str and len(subterm)>1:
		                                      
		                                      if subterm not in csvdict.keys():
		                                              
		                                              csvdict[subterm]=copy.deepcopy(ontostruct)
		                                              csvdict[subterm]["provenance"] = []
		                                      
		                                      if len(csvdict[row[0]]["provenance"])>0:
		                                              
		                                              csvdict[subterm]["provenance"].append("is split from ["+ csvdict[row[0]]["provenance"][0] +"]: " + row[0])
		                                              
		                                      else:
		                                              
		                                              csvdict[subterm]["provenance"].append("is split from [lack provenance info]: " + row[0])

	except IOError:

		pass

	my_file.close()
	
	return csvdict

						
def getSPARQLResults(csvdict, qscope):
	''' 
	Function to engage sparql query of putative contents from batch of annotations
	 specific to each selected ontology and that relate to each successive term.
	
	csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key. Tip: generate using openCSVFile function which
	 requires a correctly formatted qscope data structure (see below).	 
	qscope: dict specifying ontologies queried from, endpoints to be used, prefixes,
	 uris, and custom list of annotation labels to be queried (field: "optional").
	 Tip: generate using openQscopeFile function.
	
	crossonto_output: dict of sparql answers covering annotation batch
	 with ontology as primary key and term as secondary key.
	'''
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
	''' 
	Function to fill-in csvdict structure with contents obtained by spqarql
	 queries across annotation labels over listed terms.
	
	csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key. Tip: generate un-filled structure using openCSVFile 
	 function which requires a correctly formatted qscope data structure.
	
	crossonto_output: dict of sparql answers covering annotation batch
	 with ontology as primary key and term as secondary key. Tip: obtain
	 by feeding co-constructed csvdict and qscope data structures to 
	 getSPARQLResults function.
	'''
	
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
                                                                
                                                                tupl = (result[res]['value'],"","")
                                                                
                                                                #Mandatory fields, intended to be "label" and "id"
                                                                if type(csvdict[i][onto+"_"+lpoi[res]]) is list:
                                                                        
                                                                        csvdict[i][onto+"_"+lpoi[res]].append( tupl )
                                                                
                                                                #Other fields, customisable via onto_and_props.csv file
                                                                elif type(csvdict[i][onto+"_"+lpoi[res]])is set:
                                                                        
                                                                        csvdict[i][onto+"_"+lpoi[res]].add( tupl )
                                                                        
                                                        else:
                                                                
                                                                print res, "not in", lpoi.keys()
                                                                
                                                else:
                                                        
                                                        pass
                                
                                #Store label returned within query as "related entry" in case match to sought term is not exact
                                else:
                                        
                                        if "related" in lpoi.keys():                                                
                                                
                                                tupl = Tuplify_LblIdDef( result )
                                                
                                                #Discard content already listed with identical label and id if it doesn't provide a missing definition
                                                list_inspect = csvdict[i][onto+"_"+lpoi["related"]]
                                                
                                                whole_new = True
                                                
                                                for ins in list_inspect:
                                                        
                                                        if ins[0]==tupl[0] and ins[1]==tupl[1]:
                                                                
                                                                if len(ins[2])>0 and len(tupl[2])>0:
                                                                        
                                                                        #keep and append
                                                                        pass
                                                                
                                                                if len(ins[2])>0 and len(tupl[2])==0:
                                                                        
                                                                        #keep do not append
                                                                        whole_new = False
                                                                        break
                                                                        
                                                                if len(ins[2])==0 and len(tupl[2])>0:
                                                                        
                                                                        #remove and append
                                                                        csvdict[i][onto+"_"+lpoi["related"]].remove( ins )
                                                                        break
                                                                
                                                                if len(ins[2])==0 and len(tupl[2])==0:
                                                                        
                                                                        #keep do not append
                                                                        whole_new = False
                                                                        break
                                                
                                                if whole_new:
                                                        
                                                        if type(csvdict[i][onto+"_"+lpoi["related"]]) is list:
                                                        
                                                                csvdict[i][onto+"_"+lpoi["related"]].append( tupl )
                                                                
                                                        elif type(csvdict[i][onto+"_"+lpoi["related"]])is set:
                                                                
                                                                csvdict[i][onto+"_"+lpoi["related"]].add( tupl )
                                                                
                                        else:
                                            
                                                print "query item not stored as related to: ", i.lower()
     	
        return csvdict


def dictToCSVfile(csvdict,file_path="csvdict.csv",verbose=False):
	''' 
	Function to write down csvdict data structure contents to a csv file.
	
	csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key. Tip: content filled-in by storeResults function or 
	 loaded from csv file using reloadFullStructureCSV function.
	'''
	    
        filename = file_path
        if "/" in file_path:
                filename = filename[::-1]
                filename = filename[:filename.index("/")]
                filename = filename[::-1]
        
        print " Writing down dictionary:", filename
    
        with open(file_path, 'wb') as csvfile:
                
                fieldnames = ['term', 'property', 'content', 'id', 'definition']
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

                        #override stricly resemblance based sorting
                        max_score = float( match_score[ max(match_score.iterkeys(), key=lambda k: match_score[k]) ] )

                        sorted_label_list = ["id", "provenance", "comment", "definition", "source", "label"]

                        for q, p in enumerate( sorted_label_list ):

                                for a in match_score.keys():
                                    
                                        if a[-len(p):]==p: 
                                                
                                                match_score[a] = max_score + (len(sorted_label_list)-q)

                                        match_score[a] = float( match_score[a] )
                        
                        match_score = sorted(match_score, key=match_score.get, reverse=True)
                                                                                        
                        # Write down in established order
                        monitorlist = []
                                            
                        for w in match_score:
                                
                                # annotations
                                for p in csvdict[k].keys():
                                        
                                        a = p
                                        if '_' in a: a = a[a.index('_')+1:]
                                        
                                        if w==a:
                                                
                                                monitorlist.append( p )
                                                newi = True
                                                
                                                # content
                                                for i in csvdict[k][p]:
                                                        
                                                        #Deal with exception non-tuple entries,
                                                        #entries in "provenance" field include in tuple
                                                        if type(i) is str: i = (i,"","")
                                                        
                                                        if newp and newi:
                                                                
                                                                if verbose: print "> ", encodeForWriting(k), "\t", encodeForWriting(p), "\t", encodeForWriting(i[0]), "\t", encodeForWriting(i[1]), "\t", encodeForWriting(i[2])
                                                                writer.writerow({'term': encodeForWriting(k), 'property': encodeForWriting(p), 'content': encodeForWriting(i[0]), 'id': encodeForWriting(i[1]), 'definition': encodeForWriting(i[2])})
                                                                newp = False
                                                                newi = False
                                                        
                                                        elif newi:
                                                                
                                                                if verbose: print "> " + " "*len(encodeForWriting(k)) + "\t", encodeForWriting(p), "\t", "\t", encodeForWriting(i[0]), "\t", encodeForWriting(i[1]), "\t", encodeForWriting(i[2])
                                                                writer.writerow({'property': encodeForWriting(p), 'content': encodeForWriting(i[0]), 'id': encodeForWriting(i[1]), 'definition': encodeForWriting(i[2])})
                                                                newi = False
                                                                
                                                        else:
                                                                
                                                                if verbose: print "> " + " "*len(encodeForWriting(k)) + "\t" + " "*len(encodeForWriting(p)) + "\t", encodeForWriting(i[0]), "\t", encodeForWriting(i[1]), "\t", encodeForWriting(i[2])
                                                                writer.writerow({'content': encodeForWriting(i[0]), 'id': encodeForWriting(i[1]), 'definition': encodeForWriting(i[2])})
    
                        #Consistency checks
                        for w in monitorlist:
                                if monitorlist.count(w)>1:
                                        print " !!! ", w, "  repeated annotation, term =", k, "  !!! "
                                if w not in csvdict[k].keys():
                                        print " !!! ", w, "  de novo annotation, term =", k, "  !!! "
                        for p in csvdict[k].keys():
                                if p not in monitorlist:
                                        print " !!! ", p, "  annotation was dropped, term =", k, "  !!! "
    
        print " Finished writing down dictionary:", filename, "\n"


def generate_SPARQL_Query(prefixes, from_uri, term, qscope={}):
	'''
	Function formatting a sparql query to gather label and id corresponding
	 to a particular term within a particular ontology. Also gathers 
	 contents of a set of "optional" annotations for this term from this
	 ontology, as specified in qscope data structure. Tip: used by getData 
	 function.
	
        prefixes: e.g. """
         prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
         prefix owl: <http://www.w3.org/2002/07/owl#>
         prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>         
         """
        
        from_uri: e.g. "http://bioportal.bioontology.org/ontologies/"
        
        term: particular term about which content corresponding to a set of 
         annotations is tentatively being queried from a particular ontology.
        
	qscope: data structure with "optional" field containing custom list of 
	 annotation labels to be included in query, as well as "noprefix" field
	 containing annotation reference IDs for those annotations from the 
	 custom list that could be identified within the particular ontology
	 being queried from.
        '''
	
	if from_uri!="":
	       
	        ##Early non-customisable query formatting
		#sparql_query = prefixes+"""
		#select ?x ?label ?def ?defsrc ?comment ?preflabel ?altterm
		#from """+from_uri+"""
		#where{
		#  ?x rdfs:label ?label.
		#  filter REGEX(?label, "%s")""" %term
        	#sparql_query += """OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000115> ?%s }""" %"def"
        	#sparql_query += """OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000119> ?%s }""" %"defsrc"
        	#sparql_query += """OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000116> ?%s }""" %"comment"
        	#sparql_query += """OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000111> ?%s }""" %"preflabel"
        	#sparql_query += """OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000118> ?%s }""" %"altterm"
		#sparql_query += """}"""
                
		sparql_query= prefixes+"""
		select ?id ?label """
		if "optional" in qscope.keys():
          		for opt in qscope["optional"]:
                                opt = formatAsRDFSpropertyLabel( opt )
                                sparql_query += """?%s """ %opt
		sparql_query += """
		from <"""+from_uri+""">
		where{"""
		if "noprefix" not in qscope.keys() and "optional" not in qscope.keys():
		      sparql_query += """?id rdfs:label ?label.
		      filter REGEX(?label, "%s")
		      """ %term
        	if "noprefix" in qscope.keys():
        	       if "optional" in qscope.keys(): sparql_query += """ { """
        	       sparql_query += """?id rdfs:label ?label.
        	       filter REGEX(?label, "%s")
        	       """ %term                	       
            	       for opt in qscope["noprefix"]:
            	               sparql_query += """OPTIONAL{ ?id <""" + opt[1] +"""> ?%s }
            	               """ %formatAsRDFSpropertyLabel( opt[0] )
		if "optional" in qscope.keys():
		      if "noprefix" in qscope.keys(): sparql_query += """ } UNION { """
		      sparql_query += """?id rdfs:label ?label.
		      filter REGEX(?label, "%s")
		      """ %term
		      for opt in qscope["optional"]:
		              opt = formatAsRDFSpropertyLabel( opt )
		              #sparql_query += """OPTIONAL{ ?id  rdf:""" + opt +""" ?%s }
		              #""" %opt
		              #sparql_query += """OPTIONAL{ ?id  owl:""" + opt +""" ?%s }
		              #""" %opt
		              sparql_query += """OPTIONAL{ ?id rdfs:""" + opt +""" ?%s }
		              """ %opt
		      if "noprefix" in qscope.keys(): sparql_query += """ } """
		sparql_query += """}"""

	else: #SPARQL Query for Neurolex
		
		if type(term) is str and len(term)>1:
		      term = term[0].upper() + term[1:]

		#term=term.capitalize()
		
		sparql_query= prefixes+"""
		select ?id ?label """
		if "optional" in qscope.keys():
          		for opt in qscope["optional"]:
                                opt = formatAsRDFSpropertyLabel( opt )
                                sparql_query += """?%s """ %opt
		sparql_query += """	
		where {
		  ?id property:Label ?label
		  filter REGEX(?label, "%s")
		""" % term
		if "optional" in qscope.keys():
        	       for opt in qscope["optional"]:
        	           
        	               opt = formatAsRDFSpropertyLabel( opt )
        	               if len(opt)>1: nlxopt = opt[0].upper() + opt[1:]
        	               
        	               sparql_query += """OPTIONAL{ ?id property:""" + nlxopt +""" ?%s }
        	               """ %opt
        	               
		sparql_query += """}"""		
		print("Je suis dans la condition Neurolex avec from_uri empty")
		
	return sparql_query


def getData(qscope, ontology, term):
        '''
        Function defining and performing sparql query on a single term.
         Tip: during execution, "qscop" data structure is used which is a
         duplicate of "qscope" with "noprefix" field restricted to the 
         annotation reference IDs identified for the particular ontology being
         queried from.
        
	qscope: dict specifying ontologies queried from, endpoints to be used, 
	 prefixes, uris, and custom list of annotation labels to be queried 
	 (field: "optional" & "noprefix"). Tip: generate using openQscopeFile 
	 function.
        
        ontology: name of particular ontology to be queried from, as indicated 
         in qscope "ontology" field. Tip: also gets concatenated to string
         from corresponding "from_uri" field of qscope.
        
        term: individual term over which the sparql query should be performed.
        
        results: data structure resulting from sparql query convert with 
         setReturnFormat as JSON.
        '''
        
        results  = {}
        
        onto_ind = qscope["ontology"].index(ontology)
        
        endpoint = ""
        
        if "endpoint" in qscope.keys():
                
                if len(qscope["endpoint"])>onto_ind:
                                            
                        endpoint = qscope["endpoint"][onto_ind]
                
        if endpoint != "":
                
                sparql=SPARQLWrapper(endpoint)
                
                if endpoint==bioportal_endpoint:
                        
                        sparql.addCustomParameter("apikey", "de9357da-d547-40be-ba80-24a3a995ffbf")
                        
                #[prefixes, from_uri]=format_SPARQL_Query(endpoint, ontology)
                
                prefixes = ""
                
                if "prefixes" in qscope.keys():
                        
                        if len(qscope["prefixes"])>onto_ind:
                                
                                prefixes = qscope["prefixes"][onto_ind]
                        
                if prefixes != "":
                        
                        from_uri = ""
                        
                        if "from_uri" in qscope.keys():
                                
                                if len(qscope["from_uri"])>onto_ind:
                                
                                        from_uri = qscope["from_uri"][onto_ind]
                       
                        if len(from_uri)>len("http://") and from_uri[:len("http://")] == "http://":
                                                                
                                from_uri = from_uri + ontology
                                
                        else:
                                
                                from_uri = ""
                        
                        #Restrict query scope to noprefixes as identified for each ontology to be queried from
                        qscop = {}
                        for k in qscope.keys():
                                if k!="noprefix":
                                        qscop[k] = qscope[k]
                        if "noprefix" in qscope.keys() and ontology in qscope["noprefix"].keys():
                                qscop["noprefix"]    = []
                                qscop["noprefix"][:] = [k for k in qscope["noprefix"][ontology]]
                        
                        sparql_query=generate_SPARQL_Query(prefixes, from_uri, term, qscop)
                
                        print(sparql_query)
                        
                        sparql.setQuery(sparql_query)
                        
                        sparql.setReturnFormat(JSON)
                        
                        results=sparql.query().convert()
                        
                        #print(type(results))
	
        return results


##########################################
#                                        #
#           SUPPORT FUNCTIONS            #
#                                        #
##########################################

def reloadFullStructureCSV(file_path="csvdict.csv"):
	'''
	Function to load up csvdict data structure contents from a csv file
	 previously written down using dictToCSVfile function.
	
	file_path: path to csv file to be loaded from, to which the contents of 
	 a csvdict data structure were exported using dictToCSVfile function.
	
	csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key.
	'''

        filename = file_path
        if "/" in file_path:
                filename = filename[::-1]
                filename = filename[:filename.index("/")]
                filename = filename[::-1]
        
        print " Loading dictionary:", filename
	
        csvdict = {}
        
        try:
                
                my_file=open(file_path, 'rb')

                csv_file=csv.reader(my_file, dialect='excel', delimiter=';')
        
                headerskip = False
                
                for row in csv_file:
                        
                        if headerskip:
                                
                                if len(row[0])>0:
                                        
                                        term  = row[0]
                                        csvdict[term] = {}
                                        
                                if len(row[1])>0:
                                        
                                        annot = row[1]
                                        csvdict[term][annot] = []
                                        
                                #if "related" not in annot:
                                if len(row)==3:
                                        
                                        csvdict[term][annot].append( row[2] )
                                        
                                elif len(row)==4:
                                        
                                        csvdict[term][annot].append( (row[2], row[3], "") )
                                        
                                elif len(row)==5:
                                    
                                        csvdict[term][annot].append( (row[2], row[3], row[4]) )
                                        
                        else:
                                
                                headerskip = True
                                
        except:
                
                print "Could not load csvdict data structure from", filename
        
        return csvdict


def dictToMappingDashboardCSV(csvdict, file_path="MappingDashboard.csv"):
	''' 
	Function to write down csvdict data structure contents to a csv file,
	 arranged to be convenient in a mapping effort.
	
        csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key. Tip: content filled-in by storeResults function or 
	 loaded from csv file using reloadFullStructureCSV function.
	'''
	
        filename = file_path
        if "/" in file_path:
                filename = filename[::-1]
                filename = filename[:filename.index("/")]
                filename = filename[::-1]
        
        print " Writing down dictionary:", filename
        
        with open(file_path, 'wb') as csvfile:
                
                #Establish header 
                fieldnames = ['term']
                temp = ['provenances', 'ids', 'defs', 'comments', 'notes', 'examples', 'sources', 'relateds']
                for k in temp:                        
                        fieldnames.append( k[:-1] + "_count" )
                        fieldnames.append( k )                             
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=';')
                writer.writeheader()
                
                fn_lookup = { fieldnames[i]: [fieldnames[i][:-1]] for i in range(len(fieldnames))}
                for k in fn_lookup.keys():                        
                        if k[-len("_count"):] == "_count" in k: fn_lookup[k] = []
                fn_lookup['term'] = []
                fn_lookup['defs'] = ['definition']
        
                # terms
                for k in csvdict.keys():
                        
                        rowdict = {}
                        rowdict['term'] = k
                        
                        #based on column header name
                        for fn in fieldnames:
                                
                                aggl_str = ""
                                aggl_list = list()                               
                                aggl_nbi  = 0
                                
                                #those with a non-empty corresponding list of lookup names
                                #(avoid "term" header and all containing "_count"
                                if len(fn_lookup[ fn ])>0:
                                        
                                        #lookup names designated as corresponding to header of interest
                                        for m in fn_lookup[fn]:
                                                
                                                #within all annotations collected for the term
                                                for j in csvdict[k].keys():
                                                        
                                                        #the end of the annotation name matches lookup name
                                                        if j[-len(m):] == m:
                                                                
                                                                if "provenance" not in fn: aggl_list.append( j )
                                                                
                                                                for i in csvdict[k][j]:
                                                                        
                                                                        if type(i) is str and i not in aggl_list:
                                                                                                                                                            
                                                                                aggl_list.append( i )
                                                                                aggl_nbi += 1
                                                                        
                                                                        elif type(i) is tuple and i[0]+" "+i[1] not in aggl_list:
                                                                                
                                                                                aggl_list.append(i[0]+" "+i[1])
                                                                                aggl_nbi += 1
                                        
                                        if aggl_nbi<=200:
                                            
                                                for m in aggl_list: aggl_str += m + " \n"                                        
                                                rowdict[fn] = aggl_str
                                                
                                        else:
                                                
                                                rowdict[fn] = "Content may exceed MS Excel cell capacity, not reported."
                                        
                                        rowdict[fn[:-1] + "_count"] = int(aggl_nbi)
                                        
                        
                        writer.writerow( rowdict )


def dictToMappingSummaryCSV(csvdict, file_path="MappingSummary.csv"):
	''' 
	Function to write down overview of mapping per input term to a csv file.
	
	csvdict: dict of dicts with terms as primary key and annotation labels 
	 as secondary key. Tip: content filled-in by storeResults function or 
	 loaded from csv file using reloadFullStructureCSV function.
	'''
	    
        filename = file_path
        if "/" in file_path:
                filename = filename[::-1]
                filename = filename[:filename.index("/")]
                filename = filename[::-1]
        
        print " Writing down dictionary:", filename
        
        with open(file_path, 'wb') as csvfile:
        
                fieldnames = ['term', 'provenance', 'direct mapping count', 'post-splitting mapping count', 'related terms count', 'post-splitting related count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=';')
                writer.writeheader()
                
                # terms
                for k in csvdict.keys():
                        
                        rowdict = {}
                        
                        if "provenance" in csvdict[k].keys() and len(csvdict[k]["provenance"])>0:

                                qualif = False
                                        
                                compare_str = ""
                                
                                for prov in csvdict[k]["provenance"]:
                                
                                        if type(prov) is str:
                                                
                                                compare_str = prov
                                        
                                        elif type(prov) is tuple:
                                                
                                                compare_str = prov[0]
                                
                                        if "is split from" not in compare_str and "unspecified provenance" not in compare_str:
                                            
                                                qualif = True
                                                break
                                
                                #is a term from the original list provided
                                if qualif:
                                        
                                        #fill-in label and provenance
                                        rowdict["term"] = k                                        
                                        
                                        if type(compare_str) is str:
                                                    
                                                rowdict["provenance"] = compare_str
                                                        
                                        elif type(compare_str) is tuple:
                                                        
                                                rowdict["provenance"] = compare_str[0]
                                        
                                        
                                        #DIRECT MAPPING COUNT & RELATED COUNT
                                        id_set  = set()
                                        rel_set = set()
                                        
                                        for j in csvdict[k].keys():
                                                
                                                if j[-len("id"):]=="id":
                                                        
                                                        for m in csvdict[k][j]:
                                                                
                                                                id_set.add( m )
                                                
                                                if j[-len("related"):]=="related":
                                                                                        
                                                        for each_id in csvdict[k][j]:
                                                                
                                                                if type(each_id) is str:
                                                                
                                                                        rel_set.add( each_id )
                                                                        
                                                                elif type(each_id) is tuple:
                                                                        
                                                                        if len(each_id)>1 and len(each_id[1])>0:
                                                                                
                                                                                rel_set.add( each_id[0] + " " + each_id[1] )
                                                                        
                                                                        elif len(each_id)>0:
                                                                                
                                                                                rel_set.add( each_id[0] )
                                                                                                                                                            
                                        rowdict["direct mapping count"] = int(len( id_set))
                                        
                                        rowdict["related terms count"]  = int(len(rel_set))

                                        
                                        #POST-SPLITTING MAPPING COUNT & POS-SPLITTING RELATED COUNT                                       
                                        id_set  = set()
                                        rel_set = set()
                                        
                                        for j in csvdict.keys():
                                                
                                                if "provenance" in csvdict[j].keys() and len(csvdict[j]["provenance"])>0:
                                                        
                                                        for m in csvdict[j]["provenance"]:
                                                                
                                                                compare_str = ""
                                                                
                                                                if type(m) is str:
                                                                        
                                                                        compare_str = m
                                                                        
                                                                elif type(m) is tuple:
                                                                        
                                                                        compare_str = m[0]
                                                                
                                                                #is issued from splitting-up the term of interest
                                                                #i.e. the term of interest is listed in provenance field
                                                                if compare_str[:len("is split from")] == "is split from" and compare_str[-(len(k)+2):] == ": " + k:
                                                                        
                                                                        for annot in csvdict[j].keys():
                                                                                
                                                                                if annot[-len("id"):]=="id":
                                                                                        
                                                                                        for each_id in csvdict[j][annot]:
                                                                                                
                                                                                                if type( each_id ) is str:
                                                                                                
                                                                                                        id_set.add( each_id )
                                                                                                
                                                                                                elif type( each_id ) is tuple:
                                                                                                        
                                                                                                        id_set.add( each_id[0] )
                                                                                                        
                                                                                if annot[-len("related"):]=="related":
                                                                                        
                                                                                        for each_id in csvdict[j][annot]:
                                                                                                
                                                                                                if type( each_id ) is str:
                                                                                                
                                                                                                        rel_set.add( each_id )
                                                                                                
                                                                                                elif type( each_id ) is tuple:
                                                                                                        
                                                                                                        if len(each_id)>1 and len(each_id[1])>0:
                                                                                                                
                                                                                                                rel_set.add( each_id[0] + " " + each_id[1] )
                                                                                                        
                                                                                                        elif len(each_id)>0:
                                                                                                                
                                                                                                                rel_set.add( each_id[0] )
                                                                        
                                                                        break
                                        
                                        rowdict["post-splitting mapping count"] = int(len( id_set))
                                        
                                        rowdict["post-splitting related count"] = int(len(rel_set))                                      
                                                                                                                        
                                        writer.writerow( rowdict )


##########################################
#                                        #
#            GLOBAL VARIABLES            #
#                                        #
##########################################

neurolex_endpoint  = "http://rdf-stage.neuinfo.org/ds/query"
bioportal_endpoint = "http://sparql.bioontology.org/sparql"
ontofox_endpoint   = "http://sparql.hegroup.org/sparql"
