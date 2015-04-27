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

#		endpoint="http://rdf-stage.neuinfo.org/ds/query"
		prefixes="""
	           prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    	           prefix owl: <http://www.w3.org/2002/07/owl#>
	           prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		"""
		from_uri="<http://bioportal.bioontology.org/ontologies/"+ontology+">"
		
	elif endpoint==ontofox_endpoint:

#		endpoint="http://sparql.hegroup.org/sparql"
		prefixes="""
	           prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    	           prefix owl: <http://www.w3.org/2002/07/owl#>
    	           prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
		"""		
		from_uri="<http://purl.obolibrary.org/obo/merged/"+ontology+">"
		
	else:
		
		print("This endpoint is not defined")
	
#	return endpoint, prefixes, from_uri
	return prefixes, from_uri
	
def generate_SPARQL_Query(prefixes, from_uri, term):
	"""
	Generate a generic SPARQL Query to gather the term_id based on the label
	"""
	
	if from_uri!="":
		sparql_query= prefixes+"""
		select ?x ?label ?def ?defsrc ?comment ?preflabel ?altterm
		from """+from_uri+"""
		where {
		?x rdfs:label ?label.
		filter REGEX(?label, "%s")
		OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000115> ?def.       }
                OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000119> ?defsrc.    }
                OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000116> ?comment.   }
                OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000111> ?preflabel. }
                OPTIONAL{ ?x <http://purl.obolibrary.org/obo/IAO_0000118> ?altterm.   }
		}""" % term

	else: #SPARQL Query for Neurolex
		
		term=term.capitalize()
		
		sparql_query= prefixes+"""
		select ?x ?label
		where {
		?x property:Label ?label
		filter REGEX(?label, "%s")}""" % term
		print("Je suis dans la condition Neurolex avec from_uri empty")
		
	return sparql_query

def getData(endpoint, ontology, term):

	sparql=SPARQLWrapper(endpoint)

	if endpoint==bioportal_endpoint:
	
		sparql.addCustomParameter("apikey", "de9357da-d547-40be-ba80-24a3a995ffbf")
			
	[prefixes, from_uri]=format_SPARQL_Query(endpoint, ontology)
	
	sparql_query=generate_SPARQL_Query(prefixes, from_uri, term)
	
	print(sparql_query)
	
	sparql.setQuery(sparql_query)
	
	sparql.setReturnFormat(JSON)
	
	results=sparql.query().convert()
	
	print(type(results))
	
	return results
	
	
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
