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



"""
Getting ontology id, definition and superClass information from various SPARQL endpoints
using a list of labels.
"""


#Algorithm:
#1. Import csv file
#2. Generate a data structure to store the different values of the csv file
#3. Create the SPARQL query using the values in csv
#4. Query SPARQL endpoint
#5. Retrieve result and generate csv file as output

# Class Sparql_generator: create the query using values extracted from csv files
# variables: prefixes, regex
#
# Class Neurolex_SPARQL: define the SPARQL format for Neurolex SPARQL endpoint


from SPARQLWrapper import SPARQLWrapper, JSON

neurolex_endpoint  = "http://rdf-stage.neuinfo.org/ds/query"
bioportal_endpoint = "http://sparql.bioontology.org/sparql"
ontofox_endpoint   = "http://sparql.hegroup.org/sparql"

def format_SPARQL_Query(endpoint, ontology):

	if endpoint==neurolex_endpoint:
		
#		endpoint="http://rdf-stage.neuinfo.org/ds/query"
		prefixes="""
		  prefix property: <http://neurolex.org/wiki/Property-3A>
		"""
		from_uri=""
	
	elif endpoint==bioportal_endpoint:

#		endpoint="http://sparql.bioontology.org/sparql"
		prefixes="""
	           prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    	           prefix owl: <http://www.w3.org/2002/07/owl#>
	           prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		"""
		from_uri="http://bioportal.bioontology.org/ontologies/"+ontology+">"
		
	elif endpoint==ontofox_endpoint:

#		endpoint="http://sparql.hegroup.org/sparql"
		prefixes="""
	           prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    	           prefix owl: <http://www.w3.org/2002/07/owl#>
    	           prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		"""
		from_uri="http://purl.obolibrary.org/obo/merged/"+ontology+">"
		
	else:
		
		print("This endpoint is not defined")
	
#	return endpoint, prefixes, from_uri
	return prefixes, from_uri
	
def generate_SPARQL_Query(prefixes, from_uri, term, qscope={}):
	"""
	Generate a generic SPARQL Query to gather the term_id based on the label
	"""
	
	if from_uri!="":
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
            	       for opt in qscope["noprefix"].keys():
            	               sparql_query += """OPTIONAL{ ?id <""" + qscope["noprefix"][opt] +"""> ?%s }
            	               """ %formatAsRDFSpropertyLabel( opt )
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
                                
                        sparql_query=generate_SPARQL_Query(prefixes, from_uri, term, qscope)
                
                        print(sparql_query)
                        
                        sparql.setQuery(sparql_query)
                        
                        sparql.setReturnFormat(JSON)
                        
                        results=sparql.query().convert()
                        
                        #print(type(results))
	
        return results


def formatAsRDFSpropertyLabel( charstr ):
    opt = charstr.split()
    op  = opt[0]
    if len(opt)>1:
        op = opt[0].lower()
        for o in opt[1:]:
            if len(o)==1:
                o = o.upper()
            elif len(o)>1:
                o = o[0].upper() + o[1:].lower()
            op = op + o
    return op

	
if __name__ == "__main__":
    sparql_service = "http://sparql.bioontology.org/sparql/"

    #To get your API key register at http://bioportal.bioontology.org/accounts/new
    api_key = "de9357da-d547-40be-ba80-24a3a995ffbf"

    #Some sample query.
    query_string = """ 
        PREFIX omv: <http://omv.ontoware.org/2005/05/ontology#>
        
        SELECT ?ont ?name ?acr
        WHERE { ?ont a omv:Ontology;
                    omv:acronym ?acr;
                    omv:name ?name .
        } 
    """
