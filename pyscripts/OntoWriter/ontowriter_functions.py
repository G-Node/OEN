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



###########################################
#                                         #
#            IMPORTED MODULES             #
#                                         #
###########################################

import os, inspect
from OWLify import OWL as OWLclass
from ontospy.ontospy import *


filename   = inspect.getframeinfo(inspect.currentframe()).filename
scriptpath = os.path.dirname(os.path.abspath(filename))
oenpath    = scriptpath[:scriptpath.find('OEN\\')+4]

os.chdir( oenpath )

from pyscripts.generic_functions.generic_functions import splitTermID, avoidSpecials


###########################################
#                                         #
#           SUPPORT FUNCTIONS             #
#                                         #
###########################################


def OENimportedClass(OWL, oen_id, ppty_dict):
    '''
    Function to add a class entry by appending required text to the doc field of 
     an owlify owl object. 
    
    OWL: instance of the owlify OWL class.
    
    oen_id: string constituted of prefix "oen_" and reference integer to be 
     attributed to the new class left padded with zeros up to seven characters,
     for a standard grand total of 11 characters.
    
    ppty_dict: dictionary with annotation properties to be included within class 
     declaration as keys, and corresponding expected content as values.
     e.g. {"obo:IAO_0000115":"A thing that is not another one", etc.}
    '''
    
    stub = '\n    <!-- ' + OWL.namespace + '/' + oen_id + ' -->\n'
    stub += '\n    <owl:Class rdf:about="&oen_term;' + oen_id + '">\n'
    for prefix in ppty_dict.keys():
        if type(ppty_dict[prefix]) is str: ppty_dict[prefix] = [ ppty_dict[prefix] ]
        if type(ppty_dict[prefix]) is list:
            for ppty in ppty_dict[prefix]:
                if type(ppty) is not str: ppty = str(ppty)
                if prefix=="rdfs:subClassOf" and ppty.lower() in ["oen_0000001", "unclassified term"]:
                    stub += '    \t<rdfs:subClassOf rdf:resource="&oen_term;oen_0000001"/>\n'
                elif prefix=="rdfs:subClassOf" and ppty[:len("oen_term:oen_")].lower() == "oen_term:oen_":
                    temp = -1
                    try:
                        temp = int( ppty[len("oen_term:oen_"):] )
                    except:
                        print "Encountered non integer value of oen id"
                        pass
                    if temp in range(10000000):
                        zeropad = "0"*(int(7) - len(str(temp)))
                        oen_idz = "oen_" + zeropad + str(temp)
                        stub += '    \t<' + prefix + ' rdf:resource="&oen_term;' + oen_idz + '"/>\n'
                    else:
                        stub += '    \t<' + prefix + ' xml:lang="en">' + avoidSpecials(ppty) + '</' + prefix + '>\n'
                else:
                    stub += '    \t<' + prefix + ' xml:lang="en">' + avoidSpecials(ppty) + '</' + prefix + '>\n'
    stub += '    </owl:Class>\n\n\n'
    print stub
    OWL.doc += stub
    return OWL


def reloadOWL(OWL,file_path="oen_term.owl"):
    '''
    Function to make the doc field of an owlify owl object the exact replica of 
     the body of a pre-existing owl file.
    
    OWL: instance of the owlify OWL class.
    
    file_path: the path to the owl file to be reloaded.
    
    '''
    filename = file_path
    if "/" in file_path:
        filename = filename[::-1]
        filename = filename[:filename.index("/")]
        filename = filename[::-1]
    try:
        with open(file_path, "r") as myfile:
            data=myfile.read()
        if "</rdf:RDF>" in data:
            fromtheend = len(data) - data.index("</rdf:RDF>")
            OWL.doc = data[:-fromtheend]
        else:
            print "Could not reload OWL from:", filename
    except:
        print "Could not reload OWL from:", filename
    return OWL


def shutOWL(OWL):
    '''
    Function to tie down doc field of an owlify owl object and write it to disk
     using the filenam specified in its outfile field.
    
    OWL: instance of the owlify owl class.
    
    '''
    filename = OWL.outfile
    if "/" in OWL.outfile:
        filename = filename[::-1]
        filename = filename[:filename.index("/")]
        filename = filename[::-1]
    try:        
        fileh = open(OWL.outfile, 'w')
        OWL.doc += '</rdf:RDF>\n'        
        fileh.write(OWL.doc)
        fileh.close()
    except:
        print "Could not shut OWL:", filename


def ontoUpdate(OWL, file_path="oen_term.owl"):
    '''
    Function to return matching OntoSPy ontology object and owlify owl object, 
     based using a pre-existing owl file as reference.
    
    OWL: instance of the owlify owl class.
        
    file_path: path to the owl file used as reference.
    
    onto: instance of the OntoSPy ontology class.
        
    '''
    
    
    filename = file_path
    if "/" in file_path:
        filename = filename[::-1]
        filename = filename[:filename.index("/")]
        filename = filename[::-1]
    try:    
        shutOWL(OWL)
        onto = Ontology(file_path)
        OWL = reloadOWL(OWL)
    except:
        print "could not update ontology:", filename
        onto = []
    return OWL, onto


def findClassIDfromLabel(onto,k):
    '''
    Function to return the set of class identifiers of all classes for which a
     rdfs:label annotation can be found that matches the spelling of the 
     provided string, within an OntoSPy ontology object.
    
    onto: instance of the OntoSPy ontology class.
        
    k: string to be matched.
    
    id_set: set of OntoSPy ontology classname identifiers.
    
    '''
    
    id_set = set()
    for clas in onto.allclasses:
        if "alltriples" in onto.classRepresentation(clas).keys():
            for tripl in onto.classRepresentation(clas)["alltriples"]:
                if tripl[0] == "rdfs:label" and tripl[1][1:-1].lower() == k.lower():
                    try:
                        id_set.add( str( onto.classRepresentation(clas)["classname"] ) )
                    except:
                        print "Class ID could not be retrieved:", onto.classRepresentation(clas)["classname"]
    return id_set


def listAlreadyUsedIDs( onto, option="" ):
    '''
    Function to return a list of the identifiers of all existing classes within
     an OntoSPy ontology object.
    
    onto: instance of the OntoSPy ontology class.
        
    option: string that can be used to specify a classname to be fully or 
     partially matched as fetching criteria.
    
    id_list: list of OntoSPy ontology classname identifiers.
    
    '''
    # classFind expected format: 
    # [rdflib.term.URIRef(u'http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000001')]
    #e.g. use as option: "oen_"
    id_list = []
    try:
        if option=="":
            for clas in onto.allclasses:
                id_list.append( onto.classRepresentation(clas)["classname"] )
        else:
            id_list = onto.classFind( option )
        id_list[:] = [int(splitTermID( str(k) )[1]) for k in id_list]
        id_list = sorted(list(set(id_list)))
    except:
        print "Could not use OntoSPy classFind()"
    return id_list


def upOENids(oen_id_free,oen_id_used):
    '''
    Function to obtain remove from a list of integers those that pertain to 
     another list.
    
    oen_id_free: list of integers that correspond to non-allocated identifiers.
    
    oen_id_used: list of integers that correspond to allocated identifiers.
    
    '''
    oen_id_free = set(oen_id_free) - set(oen_id_used)
    return sorted(list(oen_id_free))
      

def OWLrestart( OWL ):
    '''
    Function to return an owlify owl object with its doc field set as the exact
     albeit rather lengthy replica of a primitive version of oen_term.owl, that
     included all necessary annotations and very few oen classes.
    
    OWL: instance of the owlify OWL class.
    
    '''
    stub = """<?xml version="1.0"?>


<!DOCTYPE rdf:RDF [
    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
    <!ENTITY obo "http://purl.obolibrary.org/obo/" >
    <!ENTITY dc "http://purl.org/dc/elements/1.1/" >
    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
    <!ENTITY protege "http://protege.stanford.edu/plugins/owl/protege#" >
    <!ENTITY oen_term "http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/" >
]>


<rdf:RDF xmlns="http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl#"
     xml:base="http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:obo="http://purl.obolibrary.org/obo/"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:protege="http://protege.stanford.edu/plugins/owl/protege#"
     xmlns:oen_term="http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <owl:Ontology rdf:about="http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl">
        <owl:versionInfo rdf:datatype="&xsd;dateTime">2015-05-28</owl:versionInfo>
        <dc:contributor>Roman Moucek</dc:contributor>
        <dc:contributor>Shreejoy Tripathy</dc:contributor>
        <dc:contributor>Anita Brandowski</dc:contributor>
        <dc:contributor>Thomas Wachtler</dc:contributor>
        <dc:creator>Yann Le Franc</dc:creator>
        <dc:contributor>Jan Grewe</dc:contributor>
        <owl:versionInfo xml:lang="en">0.1</owl:versionInfo>
        <dc:contributor>Petr Bruha</dc:contributor>
        <dc:identifier>http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl</dc:identifier>
        <dc:contributor>Antoine Bremaud</dc:contributor>
        <dc:title xml:lang="en">Terminology of the Ontology for Experimental Neurophysiology</dc:title>
        <dc:contributor>Vaclav Papez</dc:contributor>
        <owl:imports rdf:resource="http://protege.stanford.edu/plugins/owl/dc/protege-dc.owl"/>
        <owl:versionIRI rdf:resource="http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl"/>
    </owl:Ontology>
    


    <!-- 
    ///////////////////////////////////////////////////////////////////////////////////////
    //
    // Annotation properties
    //
    ///////////////////////////////////////////////////////////////////////////////////////
     -->

    <owl:AnnotationProperty rdf:about="&dc;description">
        <rdfs:label>Description</rdfs:label>
        <rdfs:label xml:lang="en-us">Description</rdfs:label>
        <rdfs:comment xml:lang="en-us">An account of the content of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Description may include but is not limited to: an abstract,
         table of contents, reference to a graphical representation
         of content or a free-text account of the content.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0100001">
        <rdfs:label xml:lang="en">term replaced by</rdfs:label>
        <obo:IAO_0000117 xml:lang="en">Person:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000119 xml:lang="en">Person:Alan Ruttenberg</obo:IAO_0000119>
        <obo:IAO_0000115 xml:lang="en">Use on obsolete terms, relating the term to another term that can be used as a substitute</obo:IAO_0000115>
        <obo:IAO_0000111 xml:lang="en">term replaced by</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000125"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;contributor">
        <rdfs:label>Contributor</rdfs:label>
        <rdfs:label xml:lang="en-us">Contributor</rdfs:label>
        <rdfs:comment xml:lang="en-us">An entity responsible for making contributions to the
         content of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Examples of a Contributor include a person, an 
         organisation, or a service.  Typically, the name of a 
         Contributor should be used to indicate the entity.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000232">
        <rdfs:label xml:lang="en">curator note</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">An administrative note of use for a curator but of no use for a user</obo:IAO_0000115>
        <obo:IAO_0000117 xml:lang="en">PERSON:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">curator note</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000589">
        <rdfs:label xml:lang="en">OBO foundry unique label</rdfs:label>
        <obo:IAO_0000116 rdf:datatype="&xsd;string">The intended usage of that property is as follow: OBO foundry unique labels are automatically generated based on regular expressions provided by each ontology, so that SO could specify unique label = &#39;sequence &#39; + [label], etc. , MA could specify &#39;mouse + [label]&#39; etc. Upon importing terms, ontology developers can choose to use the &#39;OBO foundry unique label&#39; for an imported term or not. The same applies to tools .</obo:IAO_0000116>
        <obo:IAO_0000115 xml:lang="en">An alternative name for a class or property which is unique across the OBO Foundry.</obo:IAO_0000115>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBO Foundry &lt;http://obofoundry.org/&gt;</obo:IAO_0000119>
        <obo:IAO_0000111 xml:lang="en">OBO foundry unique label</obo:IAO_0000111>
        <obo:IAO_0000117 xml:lang="en">PERSON:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Bjoern Peters</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Chris Mungall</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Melanie Courtot</obo:IAO_0000117>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000125"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000231">
        <rdfs:label xml:lang="en">has obsolescence reason</rdfs:label>
        <obo:IAO_0000117 xml:lang="en">PERSON:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Melanie Courtot</obo:IAO_0000117>
        <obo:IAO_0000115 xml:lang="en">Relates an annotation property to an obsolescence reason. The values of obsolescence reasons come from a list of predefined terms, instances of the class obsolescence reason specification.</obo:IAO_0000115>
        <obo:IAO_0000111 xml:lang="en">has obsolescence reason</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;creator">
        <rdfs:label>Creator</rdfs:label>
        <rdfs:label xml:lang="en-us">Creator</rdfs:label>
        <rdfs:comment xml:lang="en-us">An entity primarily responsible for making the content 
         of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Examples of a Creator include a person, an organisation,
         or a service.  Typically, the name of a Creator should 
         be used to indicate the entity.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;subject">
        <rdfs:label>Subject and Keywords</rdfs:label>
        <rdfs:label xml:lang="en-us">Subject and Keywords</rdfs:label>
        <rdfs:comment xml:lang="en-us">The topic of the content of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Typically, a Subject will be expressed as keywords,
         key phrases or classification codes that describe a topic
         of the resource.  Recommended best practice is to select 
         a value from a controlled vocabulary or formal 
         classification scheme.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;OBI_9991118">
        <rdfs:label rdf:datatype="&xsd;string">IEDB alternative term</rdfs:label>
        <obo:IAO_0000115 rdf:datatype="&xsd;string">An alternative term used by the IEDB.</obo:IAO_0000115>
        <obo:IAO_0000119 rdf:datatype="&xsd;string">IEDB</obo:IAO_0000119>
        <obo:IAO_0000111 rdf:datatype="&xsd;string">IEDB alternative term</obo:IAO_0000111>
        <obo:IAO_0000117 rdf:datatype="&xsd;string">PERSON:Randi Vita, Jason Greenbaum, Bjoern Peters</obo:IAO_0000117>
        <rdfs:subPropertyOf rdf:resource="&obo;IAO_0000118"/>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&rdfs;comment"/>
    <owl:AnnotationProperty rdf:about="&obo;OBI_9991119">
        <rdfs:label rdf:datatype="&xsd;string">FGED alternative term</rdfs:label>
        <obo:IAO_0000115 rdf:datatype="&xsd;string">An alternative term used by the Functional Genomics Data (FGED) Society.</obo:IAO_0000115>
        <obo:IAO_0000111 rdf:datatype="&xsd;string">FGED alternative term</obo:IAO_0000111>
        <obo:IAO_0000117 rdf:datatype="&xsd;string">PERSON: Chris Stoeckert, Jie Zheng</obo:IAO_0000117>
        <obo:IAO_0000119 rdf:datatype="&xsd;string">Penn Group</obo:IAO_0000119>
        <rdfs:subPropertyOf rdf:resource="&obo;IAO_0000118"/>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0010000">
        <rdfs:label>axiom id</rdfs:label>
        <obo:IAO_0000111>axiom id</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&rdfs;isDefinedBy"/>
    <owl:AnnotationProperty rdf:about="&dc;identifier">
        <rdfs:label>Resource Identifier</rdfs:label>
        <rdfs:label xml:lang="en-us">Resource Identifier</rdfs:label>
        <rdfs:comment xml:lang="en-us">An unambiguous reference to the resource within a given context.</rdfs:comment>
        <dc:description xml:lang="en-us">Recommended best practice is to identify the resource by means
         of a string or number conforming to a formal identification
         system.
         Example formal identification systems include the Uniform
         Resource Identifier (URI) (including the Uniform Resource
         Locator (URL)), the Digital Object Identifier (DOI) and the
         International Standard Book Number (ISBN).</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;date">
        <rdfs:label>Date</rdfs:label>
        <rdfs:label xml:lang="en-us">Date</rdfs:label>
        <rdfs:comment xml:lang="en-us">A date associated with an event in the life cycle of the
         resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Typically, Date will be associated with the creation or
         availability of the resource.  Recommended best practice
         for encoding the date value is defined in a profile of
         ISO 8601 [W3CDTF] and follows the YYYY-MM-DD format.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;title">
        <rdfs:label>Title</rdfs:label>
        <rdfs:label xml:lang="en-us">Title</rdfs:label>
        <dc:description xml:lang="en-us">
        Typically, a Title will be a name by which the resource is
         formally known.
    </dc:description>
        <rdfs:comment xml:lang="en-us">A name given to the resource.</rdfs:comment>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&protege;defaultLanguage"/>
    <owl:AnnotationProperty rdf:about="&dc;relation">
        <rdfs:label>Relation</rdfs:label>
        <rdfs:label xml:lang="en-us">Relation</rdfs:label>
        <dc:description xml:lang="en-us">
         Recommended best practice is to reference the resource by means
         of a string or number conforming to a formal identification
         system.
    </dc:description>
        <rdfs:comment xml:lang="en-us">A reference to a related resource.</rdfs:comment>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;OBI_0001886">
        <rdfs:label xml:lang="en">NIAID GSCID-BRC alternative term</rdfs:label>
        <obo:IAO_0000115>An alternative term used by the National Institute of Allergy and Infectious Diseases (NIAID) Genomic Sequencing Centers for Infectious Diseases (GSCID) and Bioinformatics Resource Centers (BRC).</obo:IAO_0000115>
        <obo:IAO_0000111 xml:lang="en">NIAID GSCID-BRC alternative term</obo:IAO_0000111>
        <obo:IAO_0000119>NIAID GSCID-BRC metadata working group</obo:IAO_0000119>
        <obo:IAO_0000117>PERSON: Chris Stoeckert, Jie Zheng</obo:IAO_0000117>
        <rdfs:subPropertyOf rdf:resource="&obo;IAO_0000118"/>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000115">
        <rdfs:label rdf:datatype="&xsd;string">definition</rdfs:label>
        <rdfs:label rdf:datatype="&xsd;string">textual definition</rdfs:label>
        <rdfs:label>definition</rdfs:label>
        <rdfs:label xml:lang="en">definition</rdfs:label>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000115 xml:lang="en">The official OBI definition, explaining the meaning of a class or property. Shall be Aristotelian, formalized and normalized. Can be augmented with colloquial definitions.</obo:IAO_0000115>
        <obo:IAO_0000115 xml:lang="en">The official definition, explaining the meaning of a class or property. Shall be Aristotelian, formalized and normalized. Can be augmented with colloquial definitions.</obo:IAO_0000115>
        <obo:IAO_0000111>definition</obo:IAO_0000111>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000424">
        <rdfs:label xml:lang="en">expand expression to</rdfs:label>
        <obo:IAO_0000117 rdf:datatype="&xsd;string">Chris Mungall</obo:IAO_0000117>
        <obo:IAO_0000115 xml:lang="en">A macro expansion tag applied to an object property (or possibly a data property)  which can be used by a macro-expansion engine to generate more complex expressions from simpler ones</obo:IAO_0000115>
        <obo:IAO_0000112 xml:lang="en">ObjectProperty: RO_0002104
Label: has plasma membrane part
Annotations: IAO_0000424 &quot;http://purl.obolibrary.org/obo/BFO_0000051 some (http://purl.obolibrary.org/obo/GO_0005886 and http://purl.obolibrary.org/obo/BFO_0000051 some ?Y)&quot;
</obo:IAO_0000112>
        <obo:IAO_0000111 xml:lang="en">expand expression to</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000116">
        <rdfs:label xml:lang="en">editor note</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">An administrative note intended for its editor. It may not be included in the publication version of the ontology, so it should contain nothing necessary for end users to understand the ontology.</obo:IAO_0000115>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obfoundry.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">editor note</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000113">
        <rdfs:label xml:lang="en">in branch</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">An annotation property indicating which module the terms belong to. This is currently experimental and not implemented yet.</obo:IAO_0000115>
        <obo:IAO_0000117 xml:lang="en">GROUP:OBI</obo:IAO_0000117>
        <obo:IAO_0000119 xml:lang="en">OBI_0000277</obo:IAO_0000119>
        <obo:IAO_0000111 xml:lang="en">in branch</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000114">
        <rdfs:label xml:lang="en">has curation status</rdfs:label>
        <obo:IAO_0000119 xml:lang="en">OBI_0000281</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Bill Bug</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Melanie Courtot</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">has curation status</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;language">
        <rdfs:label>Language</rdfs:label>
        <rdfs:label xml:lang="en-us">Language</rdfs:label>
        <rdfs:comment xml:lang="en-us">A language of the intellectual content of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Recommended best practice is to use RFC 3066 [RFC3066],
         which, in conjunction with ISO 639 [ISO639], defines two-
         and three-letter primary language tags with optional
         subtags.  Examples include &quot;en&quot; or &quot;eng&quot; for English,
         &quot;akk&quot; for Akkadian, and &quot;en-GB&quot; for English used in the
         United Kingdom.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000119">
        <rdfs:label xml:lang="en">definition source</rdfs:label>
        <obo:IAO_0000119 rdf:datatype="&xsd;string">Discussion on obo-discuss mailing-list, see http://bit.ly/hgm99w</obo:IAO_0000119>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">definition source</obo:IAO_0000111>
        <obo:IAO_0000115 xml:lang="en">formal citation, e.g. identifier in external database to indicate / attribute source(s) for the definition. Free text indicate / attribute source(s) for the definition. EXAMPLE: Author Name, URI, MeSH Term C04, PUBMED ID, Wiki uri on 31.01.2007</obo:IAO_0000115>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;type">
        <rdfs:label>Resource Type</rdfs:label>
        <rdfs:label xml:lang="en-us">Resource Type</rdfs:label>
        <rdfs:comment xml:lang="en-us">The nature or genre of the content of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Type includes terms describing general categories, functions,
         genres, or aggregation levels for content. Recommended best
         practice is to select a value from a controlled vocabulary
         (for example, the DCMI Type Vocabulary [DCMITYPE]). To 
         describe the physical or digital manifestation of the 
         resource, use the Format element.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000427">
        <rdfs:label xml:lang="en">antisymmetric property</rdfs:label>
        <obo:IAO_0000117 xml:lang="en">Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">antisymmetric property</obo:IAO_0000111>
        <obo:IAO_0000112 xml:lang="en">part_of antisymmetric property xsd:true</obo:IAO_0000112>
        <obo:IAO_0000115 xml:lang="en">use boolean value xsd:true to indicate that the property is an antisymmetric property</obo:IAO_0000115>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000117">
        <rdfs:label xml:lang="en">term editor</rdfs:label>
        <obo:IAO_0000116 xml:lang="en">20110707, MC: label update to term editor and definition modified accordingly. See http://code.google.com/p/information-artifact-ontology/issues/detail?id=115.</obo:IAO_0000116>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000115 xml:lang="en">Name of editor entering the term in the file. The term editor is a point of contact for information regarding the term. The term editor may be, but is not always, the author of the definition, which may have been worked upon by several people</obo:IAO_0000115>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">term editor</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000426">
        <rdfs:label xml:lang="en">first order logic expression</rdfs:label>
        <obo:IAO_0000117 xml:lang="en">PERSON:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">first order logic expression</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000118">
        <rdfs:label xml:lang="en">alternative term</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">An alternative name for a class or property which means the same thing as the preferred name (semantically equivalent)</obo:IAO_0000115>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">alternative term</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000125"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000425">
        <rdfs:label xml:lang="en">expand assertion to</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">A macro expansion tag applied to an annotation property which can be expanded into a more detailed axiom.</obo:IAO_0000115>
        <obo:IAO_0000117 xml:lang="en">Chris Mungall</obo:IAO_0000117>
        <obo:IAO_0000112 xml:lang="en">ObjectProperty: RO???
Label: spatially disjoint from
Annotations: expand_assertion_to &quot;DisjointClasses: (http://purl.obolibrary.org/obo/BFO_0000051 some ?X)  (http://purl.obolibrary.org/obo/BFO_0000051 some ?Y)&quot;
</obo:IAO_0000112>
        <obo:IAO_0000111 xml:lang="en">expand assertion to</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;source">
        <rdfs:label>Source</rdfs:label>
        <rdfs:label xml:lang="en-us">Source</rdfs:label>
        <rdfs:comment xml:lang="en-us">A reference to a resource from which the present resource
         is derived.</rdfs:comment>
        <dc:description xml:lang="en-us">The present resource may be derived from the Source resource
         in whole or in part.  Recommended best practice is to reference
         the resource by means of a string or number conforming to a
         formal identification system.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000111">
        <rdfs:label xml:lang="en">editor preferred label</rdfs:label>
        <rdfs:label>editor preferred term</rdfs:label>
        <rdfs:label xml:lang="en">editor preferred term</rdfs:label>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000115 xml:lang="en">The concise, meaningful, and human-friendly name for a class or property preferred by the ontology developers. (US-English)</obo:IAO_0000115>
        <obo:IAO_0000111 xml:lang="en">editor preferred label</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000112">
        <rdfs:label xml:lang="en">example of usage</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">A phrase describing how a class name should be used. May also include other kinds of examples that facilitate immediate understanding of a class semantics, such as widely known prototypical subclasses or instances of the class. Although essential for high level terms, examples for low level terms (e.g., Affymetrix HU133 array) are not</obo:IAO_0000115>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Daniel Schober</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">example of usage</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;OBI_0001847">
        <rdfs:label xml:lang="en">ISA alternative term</rdfs:label>
        <obo:IAO_0000116>Requested by Alejandra Gonzalez-Beltran
https://sourceforge.net/tracker/?func=detail&amp;aid=3603413&amp;group_id=177891&amp;atid=886178</obo:IAO_0000116>
        <obo:IAO_0000111 xml:lang="en">ISA alternative term</obo:IAO_0000111>
        <obo:IAO_0000117>Person: Philippe Rocca-Serra</obo:IAO_0000117>
        <obo:IAO_0000119>ISA tools project (http://isa-tools.org)</obo:IAO_0000119>
        <obo:IAO_0000117>Person: Alejandra Gonzalez-Beltran</obo:IAO_0000117>
        <obo:IAO_0000115>An alternative term used by the ISA tools project (http://isa-tools.org).</obo:IAO_0000115>
        <rdfs:subPropertyOf rdf:resource="&obo;IAO_0000118"/>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;publisher">
        <rdfs:label>Publisher</rdfs:label>
        <rdfs:label xml:lang="en-us">Publisher</rdfs:label>
        <rdfs:comment xml:lang="en-us">An entity responsible for making the resource available</rdfs:comment>
        <dc:description xml:lang="en-us">Examples of a Publisher include a person, an organisation,
         or a service.
         Typically, the name of a Publisher should be used to
         indicate the entity.</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&rdfs;label">
        <rdfs:label>label</rdfs:label>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;coverage">
        <rdfs:label>Coverage</rdfs:label>
        <rdfs:label xml:lang="en-us">Coverage</rdfs:label>
        <dc:description xml:lang="en-us">Coverage will typically include spatial location (a place name
         or geographic coordinates), temporal period (a period label,
         date, or date range) or jurisdiction (such as a named
         administrative entity).
         Recommended best practice is to select a value from a
         controlled vocabulary (for example, the Thesaurus of Geographic
         Names [TGN]) and that, where appropriate, named places or time
         periods be used in preference to numeric identifiers such as
         sets of coordinates or date ranges.</dc:description>
        <rdfs:comment xml:lang="en-us">The extent or scope of the content of the resource.</rdfs:comment>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&owl;versionInfo"/>
    <owl:AnnotationProperty rdf:about="&rdfs;seeAlso"/>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000411">
        <rdfs:label rdf:datatype="&xsd;string">is denotator type</rdfs:label>
        <obo:IAO_0000117 rdf:datatype="&xsd;string">Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000116 rdf:datatype="&xsd;string">In OWL 2 add AnnotationPropertyRange(&#39;is denotator type&#39; &#39;denotator type&#39;)</obo:IAO_0000116>
        <obo:IAO_0000111 rdf:datatype="&xsd;string">is denotator type</obo:IAO_0000111>
        <obo:IAO_0000115 rdf:datatype="&xsd;string">relates an class defined in an ontology, to the type of it&#39;s denotator</obo:IAO_0000115>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000599">
        <rdfs:label xml:lang="en">has ID prefix</rdfs:label>
        <obo:IAO_0000115>Relates an ontology used to record id policy to a prefix concatenated with an integer in the id range (left padded with &quot;0&quot;s to make this many digits) to construct an ID for a term being created.</obo:IAO_0000115>
        <obo:IAO_0000112>Ontology: &lt;http://purl.obolibrary.org/obo/ro/idrange/&gt;
  Annotations: 
     &#39;has ID prefix&#39;: &quot;http://purl.obolibrary.org/obo/RO_&quot;
     &#39;has ID digit count&#39; : 7,
     rdfs:label &quot;RO id policy&quot;
     &#39;has ID policy for&#39;: &quot;RO&quot;</obo:IAO_0000112>
        <obo:IAO_0000117>Person:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">has ID prefix</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000598">
        <rdfs:label>has ID policy for</rdfs:label>
        <obo:IAO_0000115>Relating an ontology used to record id policy to the ontology namespace whose policy it manages</obo:IAO_0000115>
        <obo:IAO_0000111>has ID policy for</obo:IAO_0000111>
        <obo:IAO_0000117>Person:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000112>Ontology: &lt;http://purl.obolibrary.org/obo/ro/idrange/&gt;
  Annotations: 
     &#39;has ID prefix&#39;: &quot;http://purl.obolibrary.org/obo/RO_&quot;
     &#39;has ID digit count&#39; : 7,
     rdfs:label &quot;RO id policy&quot;
     &#39;has ID policy for&#39;: &quot;RO&quot;</obo:IAO_0000112>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000412">
        <rdfs:label xml:lang="en">imported from</rdfs:label>
        <obo:IAO_0000115 xml:lang="en">For external terms/classes, the ontology from which the term was imported</obo:IAO_0000115>
        <obo:IAO_0000119 xml:lang="en">GROUP:OBI:&lt;http://purl.obolibrary.org/obo/obi&gt;</obo:IAO_0000119>
        <obo:IAO_0000117 xml:lang="en">PERSON:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000117 xml:lang="en">PERSON:Melanie Courtot</obo:IAO_0000117>
        <obo:IAO_0000111 xml:lang="en">imported from</obo:IAO_0000111>
        <obo:IAO_0000114 rdf:resource="&obo;IAO_0000125"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000597">
        <rdfs:label xml:lang="en">has ID range allocated to</rdfs:label>
        <obo:IAO_0000117>Person:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000112>Datatype: idrange:1
Annotations: &#39;has ID range allocated to&#39;: &quot;Chris Mungall&quot;
EquivalentTo: xsd:integer[&gt; 2151 , &lt;= 2300]
</obo:IAO_0000112>
        <obo:IAO_0000115>Relates a datatype that encodes a range of integers to the name of the person or organization who can use those ids constructed in that range to define new terms</obo:IAO_0000115>
        <obo:IAO_0000111 xml:lang="en">has ID range allocated to</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&obo;IAO_0000596">
        <rdfs:label xml:lang="en">has ID digit count</rdfs:label>
        <obo:IAO_0000112>Ontology: &lt;http://purl.obolibrary.org/obo/ro/idrange/&gt;
  Annotations: 
     &#39;has ID prefix&#39;: &quot;http://purl.obolibrary.org/obo/RO_&quot;
     &#39;has ID digit count&#39; : 7,
     rdfs:label &quot;RO id policy&quot;
     &#39;has ID policy for&#39;: &quot;RO&quot;</obo:IAO_0000112>
        <obo:IAO_0000117>Person:Alan Ruttenberg</obo:IAO_0000117>
        <obo:IAO_0000115>Relates an ontology used to record id policy to the number of digits in the URI. The URI is: the &#39;has ID prefix&quot; annotation property value concatenated with an integer in the id range (left padded with &quot;0&quot;s to make this many digits)</obo:IAO_0000115>
        <obo:IAO_0000111 xml:lang="en">has ID digit count</obo:IAO_0000111>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;format">
        <rdfs:label>Format</rdfs:label>
        <rdfs:label xml:lang="en-us">Format</rdfs:label>
        <rdfs:comment xml:lang="en-us">The physical or digital manifestation of the resource.</rdfs:comment>
        <dc:description xml:lang="en-us">Typically, Format may include the media-type or dimensions of
         the resource. Format may be used to determine the software,
         hardware or other equipment needed to display or operate the
         resource. Examples of dimensions include size and duration.
         Recommended best practice is to select a value from a
         controlled vocabulary (for example, the list of Internet Media
         Types [MIME] defining computer media formats).</dc:description>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    <owl:AnnotationProperty rdf:about="&dc;rights">
        <rdfs:label>Rights Management</rdfs:label>
        <rdfs:label xml:lang="en-us">Rights Management</rdfs:label>
        <dc:description xml:lang="en-us">
          Typically, a Rights element will contain a rights 
          management statement for the resource, or reference 
          a service providing such information. Rights information 
          often encompasses Intellectual Property Rights (IPR), 
          Copyright, and various Property Rights. 
          If the Rights element is absent, no assumptions can be made 
          about the status of these and other rights with respect to 
          the resource.
    </dc:description>
        <rdfs:comment xml:lang="en-us">Information about rights held in and over the resource.</rdfs:comment>
        <rdfs:isDefinedBy rdf:resource="http://purl.org/dc/elements/1.1/"/>
    </owl:AnnotationProperty>
    


    <!-- 
    ///////////////////////////////////////////////////////////////////////////////////////
    //
    // Datatypes
    //
    ///////////////////////////////////////////////////////////////////////////////////////
     -->

    


    <!-- 
    ///////////////////////////////////////////////////////////////////////////////////////
    //
    // Classes
    //
    ///////////////////////////////////////////////////////////////////////////////////////
     -->

    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000001 -->

    <owl:Class rdf:about="&oen_term;oen_0000001">
        <rdfs:label xml:lang="en">unclassified term</rdfs:label>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000002 -->

    <owl:Class rdf:about="&oen_term;oen_0000002">
        <rdfs:label xml:lang="en">recording cap</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
        <rdfs:comment xml:lang="en">has quality size</rdfs:comment>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000003 -->

    <owl:Class rdf:about="&oen_term;oen_0000003">
        <rdfs:label xml:lang="en">blood pressure sensor</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000004 -->

    <owl:Class rdf:about="&oen_term;oen_0000004">
        <rdfs:label xml:lang="en">car simulator</rdfs:label>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&oen_term;oen_0000007"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&oen_term;oen_0000006"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&obo;OBI_0400107"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&oen_term;oen_0000008"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&oen_term;oen_0000013"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&oen_term;oen_0000012"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&obo;BFO_0000051"/>
                <owl:someValuesFrom rdf:resource="&oen_term;oen_0000005"/>
            </owl:Restriction>
        </owl:equivalentClass>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000005 -->

    <owl:Class rdf:about="&oen_term;oen_0000005">
        <rdfs:label xml:lang="en">bodywork</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000006 -->

    <owl:Class rdf:about="&oen_term;oen_0000006">
        <rdfs:label xml:lang="en">steering wheel</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000007 -->

    <owl:Class rdf:about="&oen_term;oen_0000007">
        <rdfs:label xml:lang="en">six-speed shifter</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000008 -->

    <owl:Class rdf:about="&oen_term;oen_0000008">
        <rdfs:label xml:lang="en">automobile pedal</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
        <obo:IAO_0000119 xml:lang="en">http://en.wikipedia.org/wiki/Automobile_pedal</obo:IAO_0000119>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000009 -->

    <owl:Class rdf:about="&oen_term;oen_0000009">
        <rdfs:label xml:lang="en">clutch pedal</rdfs:label>
        <rdfs:subClassOf rdf:resource="&oen_term;oen_0000008"/>
        <obo:IAO_0000115 xml:lang="en">clutch pedal is an automobile pedal which controls the clutch</obo:IAO_0000115>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000010 -->

    <owl:Class rdf:about="&oen_term;oen_0000010">
        <rdfs:label xml:lang="en">brake pedal</rdfs:label>
        <rdfs:subClassOf rdf:resource="&oen_term;oen_0000008"/>
        <obo:IAO_0000115 xml:lang="en">the brake pedal is an automobile pedal which controls the brakes</obo:IAO_0000115>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000011 -->

    <owl:Class rdf:about="&oen_term;oen_0000011">
        <rdfs:label xml:lang="en">gas pedal</rdfs:label>
        <rdfs:subClassOf rdf:resource="&oen_term;oen_0000008"/>
        <obo:IAO_0000118 xml:lang="en">accelerator</obo:IAO_0000118>
        <obo:IAO_0000115 xml:lang="en">the gas pedal is an automobile pedal which controls fuel and air supply to the automobile&#39;s engine</obo:IAO_0000115>
        <obo:IAO_0000118 xml:lang="en">throttle</obo:IAO_0000118>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000012 -->

    <owl:Class rdf:about="&oen_term;oen_0000012">
        <rdfs:label xml:lang="en">multimedia projector</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000013 -->

    <owl:Class rdf:about="&oen_term;oen_0000013">
        <rdfs:label xml:lang="en">web camera</rdfs:label>
        <rdfs:subClassOf rdf:resource="&obo;OBI_0000968"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000014 -->

    <owl:Class rdf:about="&oen_term;oen_0000014">
        <rdfs:label xml:lang="en">USB2 adaptor syncbox</rdfs:label>
        <rdfs:subClassOf rdf:resource="&oen_term;oen_0000001"/>
    </owl:Class>
    


    <!-- http://purl.org/incf/ontology/ExperimentalNeurophysiology/oen_term.owl/oen_0000015 -->

    <owl:Class rdf:about="&oen_term;oen_0000015">
        <rdfs:label xml:lang="en">electrod input box</rdfs:label>
        <rdfs:subClassOf rdf:resource="&oen_term;oen_0000001"/>
    </owl:Class>

    """
    OWL.doc = stub + "\n"
    return OWL



'''
###########################################
#                                         #
#                ENABLE TO                #
#  IMPORT OEN TERMS FROM CONCEPT BRANCH   #
#                                         #
###########################################

#manage oen id namespace
oen_id_free = range(10000000)
oen_id_used = [i for j in (range(1000), range(2001,10000000)) for i in j]
#oen_id_used = [i for j in (oen_id_used, listAlreadyUsedIDs(onto, "oen_")) for i in j]
oen_id_used = sorted(list(set( oen_id_used )))
oen_id_free = upOENids(oen_id_free, oen_id_used)

#Load all infos from oen_ConceptBranch.csv
header = ImportHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/oen_ConceptBranch.csv", ",")
oen_CB = LoadCSVwithHeader("/Users/Asus/Documents/GitHub/OEN/pyscripts/OntoMapper/oen_ConceptBranch.csv", header, ",")

conv_dict = {"rdfs:label":"Label", \
"rdfs:subClassOf":"SuperCategory", \
"obo:IAO_0000115":"Definition", \
"obo:IAO_0000119":"DefiningCitation", \
"obo:IAO_0000118":"Synonym"}

for term in oen_CB:
    ppty_dict = {}
    if "Id" in term.keys() and type(term["Id"]) is str and term["Id"][:len("oen_")]=="oen_":
        oen_id = -1
        try:
            oen_id = int(term["Id"][len("oen_"):])
        except:
            print "could not identify oen_id for:", term["Id"]
        if oen_id==-1 or oen_id in oen_id_used:
            if oen_id in listAlreadyUsedIDs(onto, "oen_"):
                zeropad = "0"*(int(7) - len(str(oen_id)))
                oen_idz = "oen_" + zeropad + str(oen_id)
                print 'Cannot attribute', term["Id"] ,'to "' + term["Label"] + '",', oen_idz, '\talready attributed.'
                #would use to display pre-existing label, but returns empty list.
                #onto.classRepresentation(str(onto.classFind(oen_idz)))["label"]
            else:
                print "oen_id either pertains to exclusion range or not a straight integer:", term["Id"]
            continue
        else:
            for c in conv_dict.keys():
                if conv_dict[c] in term.keys():
                    str_list = term[ conv_dict[c] ].split(",:Category:")
                    str_list[:] = [str_list[k].replace(":Category:","") for k in range(len(str_list)) if str_list[k]!=""]
                    if len(str_list)>0:
                        ppty_dict[ c ] = [] 
                        for s in str_list:
                            ppty_dict[ c ].append( s )
            if "rdfs:subClassOf" not in ppty_dict.keys() or len(ppty_dict["rdfs:subClassOf"])<1:
                ppty_dict[ "rdfs:subClassOf" ] = ["unclassified term"]
            else:
                (out, onto) = ontoUpdate(out, "C:\Users\Asus\Documents\Github\OEN\pyscripts\OntoMapper\oen_term.owl")
                temp_list = []
                for k in ppty_dict["rdfs:subClassOf"]:
                    if type(k) is str and len(k)>0:
                        id_set = findClassIDfromLabel(onto,k)
                        for each_id in id_set:
                            temp_list.append( each_id )
                ppty_dict[ "rdfs:subClassOf" ] = list(set(temp_list))
            if len(ppty_dict[ "rdfs:subClassOf" ])==0:
                ppty_dict[ "rdfs:subClassOf" ] = ["unclassified term"]
                
            zeropad = "0"*(int(7) - len(str(oen_id)))
            oen_idz = "oen_" + zeropad + str(oen_id)
            out = OENimportedClass(out, oen_idz, ppty_dict)
            oen_id_used.append( oen_id )
            oen_id_free.remove( oen_id )
'''

