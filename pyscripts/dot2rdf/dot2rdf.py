#!/usr/bin/env python2.7
# encoding: utf-8

###################################################################################
#                                                                                 #
# Work on Ontology for Experimental Neurophysiology (c) by <ylefranc> and <ant1b> #
#                                                                                 #
# This work is licensed under a                                                   #
#  Creative Commons Attribution 4.0 International License.                        #
#                                                                                 #
# You should have received a copy of the license along with this                  #
#  work. If not, see <http://creativecommons.org/licenses/by/4.0/>.               #
#                                                                                 #
###################################################################################

#abremaud@esciencefactory.com 20160105

import csv, sys

# OntoSPy v1.6.4.3
from ontospy import ontospy


def matchOntoClassLabel(term, graph):
    '''

    Lists the ids of ontology classes whose label matches input string parameter.

    Lowercase character sequence match must be exact.

    :param term: string
    :param graph: OntoSPy graph
    :return match_list:

    '''

    match_list = []

    for c in graph.classes:

         if c.bestLabel().lower().strip() == term.lower().strip():

             match_list.append( c )

    return match_list


def matchOntoPropLabel(term, graph):
    '''

    Lists the ids of ontology properties whose label matches input parameter "term".

    Lowercase character sequence match must be exact.

    :param term: string
    :param graph: OntoSpy graph
    :return match_list:

    '''

    match_list = []

    for p in graph.properties:

         if p.bestLabel().lower().strip() == term.lower().strip():

             match_list.append( p )

    return match_list


def appendGraphList( gl, filepath ):
    '''
    Load-up ontology owl file as OntoSPy graph and appends to list.

    Dependency: OntoSPy (v1.6.4.3)

    :param gl: list
    :param filepath: string
    :return out: list with OntoSPy graph appended

    '''

    out = None

    try:

        if filepath:

            if type(gl) is list and type(filepath) is str:

                if len(filepath)>0:

                    out = gl

                    g = ontospy.Graph( filepath )

                    out.append( g )

    except:

        pass

    if not out:

        print "Could not append graphs list with:", filepath

    return out


def csv2list( filepath ):
    '''
    Load csv-formatted file and returns list of line contents.
    Used in dot2rdf.py on a file where local file paths were referenced one per line.

    Dependency: csv (python module)

    :param filepath:
    :return out: list of one list per line

    '''

    out = None

    try:

        with open( filepath, 'rb') as csvfile:
            temp = csv.reader( csvfile )
            out = []
            for row in temp:
                out.append(row)

    except:

        print "Could not load CSV file:", filepath
        pass

    return out


def reportOutcome(in_set, out_set):
    '''
    On-screen report outcome of translating from dot to rdf using ontology

    :param in_set:
        Set of tuples with elements entity_iri and entity_label.
        Corresponding to entities identified from the reference ontologies.

    :param out_set:
        Set of tuples with elements "property" or "class" and entity_label.
        Corresponding labels not sported by any entity from the reference ontologies.

    '''

    try:

        print "\n" + " #" * 30 + "\n"

        print " Total node or edge labels used in graph:\t", len(in_set) + len(out_set)
        print " Node or edge labels identified in ontology:\t", len(in_set), "/", len(in_set) + len(out_set)
        print " Node or edge labels not found in ontology:\t", len(out_set), "/", len(in_set) + len(out_set)

        print "\n CONCLUSION"
        if len(out_set) == 0:
            print "  All labels used for nodes and edges have found a match in the reference ontology."
            print "  As a consequence, the generated RDF file is expected to be valid."
        else:
            print "  Some of the labels used for nodes and edges have no match in the reference ontology."
            print "  As a consequence, the generated RDF file is not expected to be valid."
            print "  Generating a valid RDF file might require that these labels, listed in:"
            print "\t" + "NeededLabelsForConsideration.csv,"
            print "  be used to create corresponding classes within the reference ontology."
            print "  This can be achieved using scripts such as:"
            print "\t" + "https://github.com/G-Node/OEN/tree/master/pyscripts/OntoMapper"
            print "  and"
            print "\t" + "https://github.com/G-Node/OEN/tree/master/pyscripts/OntoWriter"

        print "\n" + " #" * 30 + "\n"

    except:

        print "Could not report on dot2rdf outcome."


def dot2rdf_main(gv_file, gl, rdf_file, missingterms_file):
    '''
    Write to rdf_file NT-triple formatted versions of node and edge relationships described in dot-formatted gv_file.

    1) Read dot-formatted file lines,
    2) Identify nodes and edge labels (in-between double quotes),
    3) Attempt to find a class or property with matching label within the reference ontologies listed (gl),
    4) Write relation to rdf_file using either, depending on whether found or not:
     a) found: ontology-originated IRI
     b) not found: raw node-or-edge label
    5) Write down "not found" labels to missingterms_file
    6) Return lists of "found" and "not-found" tuples: [(IRI,label)  ("property"/"class",label)

    :param gv_file: python opened dot-formatted file for reading
    :param gl: list of reference ontology graphs
    :param rdf_file: python opened file for writing NT-triple formatted RDF relations
    :param missingterms_file: python opened file for writing node-or-edge labels not sported by any ontology entity
    :return [entitytuple_set, missingterms_set]: lists of tuples (see 6) above)

    '''

    out = None

    try:

        entitytuple_set = set()

        missingterms_set = set()

        for line in gv_file.readlines():

            #print line

            # In a dot-formatted graph, node and edge labels are contained in-between double quotes.
            if line[0] == '"':

                collec_array = []

                term = ""

                inbetween = False

                for c in line:

                    if len(collec_array)>2:

                        # Write down rdf triples using ontology entities IRIs or graph label when
                        # no ontology class could be found with a matching label.
                        print "<" + collec_array[0] + "> " + " <" + collec_array[2] + "> " + " <" + collec_array[1] + ">"
                        rdf_file.write("<" + collec_array[0] + "> " + " <" + collec_array[2] + "> " + " <" + collec_array[1] + "> .\n")

                        break

                    else:

                        if c == '"' and inbetween:

                            inbetween = False

                            term = term.strip()
                            term = term[term.find(":")+1:] # Avoid graph custom prefixes
                            term = term.replace('_',' ')

                            ml = []
                            # Last of 3 labels expected to be that of an edge i.e. property/predicate
                            if len(collec_array) == 2:

                                # Seek an ontology property by its name
                                for g in gl:

                                    if ml==[]: ml = matchOntoPropLabel(term.strip(), g)
                                    else: break

                            # Otherwise look for a class label
                            else:

                                # Seek an ontology class by its name
                                for g in gl:

                                    if ml==[]: ml = matchOntoClassLabel(term.strip(), g)
                                    else: break


                            if len(ml)>0:

                                term = ml[0].uri

                                entitytuple_set.add( (ml[0].uri, ml[0].bestLabel()) )

                            elif len(collec_array) == 2:

                                missingterms_set.add( ('property', term.strip()) )

                            else:

                                missingterms_set.add( ('class', term.strip()) )

                            collec_array.append( term.strip() )

                            term = ""

                        else:

                            if c=='"' and not inbetween:

                                inbetween = True

                            elif inbetween:

                                term += c

        # Write down the labels of the ontology entities that were FOUND
        # with labels matching those of nodes and edges used in the graph.
        for e in entitytuple_set:

            rdf_file.write('<' + e[0] + '> ' + ' <http://www.w3.org/2000/01/rdf-schema#label> "' + e[1] + '" .\n')

        # Write down the node and edge labels used in the graph that were NOT FOUND in ontology
        for e in missingterms_set:

            if e[0] == 'property':

                missingterms_file.write(e[1] + '\n')

        for e in missingterms_set:

            if e[0] == 'class':

                missingterms_file.write(e[1] + '\n')

        out = [entitytuple_set, missingterms_set]

    except:

        print "Could not process dot2rdf_main."

    return out



if __name__ == '__main__':
    '''
    Limitation: not designed to handle subgraphs.

    Process:
    pre) Install ontospy (developed and tested with v1.6.4.3)
    1) Put dot2rdf.py file in a local folder
    2) Create folder named "data" next to dot2rdf.py i.e. in that same local folder
    3) Create folders named "input" and "output" inside folder called "data"
    4) Create a text file named "ontology_filepaths" inside folder called "input"
    5) Write down filepaths to local ontology owl files one per line in "ontology_filepaths" file
    6) In terminal type:

        python2 dot2rdf.py path_to_dot_formatted_file

        (replacing path-etc. by the actual local path to dot-formatted file e.g. graphviz .gv).

    7) Script should work and proceed to output files in directory: /data/output.
    8) If only few unidentified labels are indicated in the on-screen report,
        manual text-editing might be the quickest way to obtain a valid RDF file,
        as opposed to the suggested method of adding terms to the reference ontologies.
    '''

    try:

        if sys.argv[1:]:

            ###################################################################################
            #                                                                                 #
            # INPUTS                                                                          #
            #                                                                                 #
            ###################################################################################

            # Open dot-formatted file
            gv_file = open( sys.argv[1] )

            #Load list of ontology filepaths
            ofpl = csv2list( "data/input/ontology_filepaths" )

            #List of reference ontologies graphs
            gl=[]
            for item in ofpl: appendGraphList(gl, item[0])


            ###################################################################################
            #                                                                                 #
            # OUTPUTS                                                                         #
            #                                                                                 #
            ###################################################################################

            # Outcome file with dot-formatted graph relations transcribed as RDF NT-triples
            rdf_file = open("data/output/gv2rdf.nt","w")

            # Outcome file with dot-formatted graph relations in which one or more member
            # was not identified within the ontology
            missingterms_file = open("data/output/NeededLabelsForConsideration.csv","w")


            ###################################################################################
            #                                                                                 #
            # PROCESS                                                                         #
            #                                                                                 #
            ###################################################################################

            [in_set, out_set] = dot2rdf_main(gv_file, gl, rdf_file, missingterms_file)

            # Report outcome of translating from dot to rdf using ontology on screen
            reportOutcome(in_set, out_set)

        else:

            print "\nPlease provide valid path to dot-formatted file as input parameter string.\n"

    except:

        print "Could not process dot2rdf."
