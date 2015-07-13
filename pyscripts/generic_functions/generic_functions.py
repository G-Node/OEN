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



def formatAsRDFSpropertyLabel( charstr ):
    '''
    e.g. "EDITOR pREferred Label" ==> "editorPreferredLabel"
    
    intended to be used as rdfs:editorPreferredLabel
    in tentative "optional" annotation sparql queries
    see generate_SPARQL_Query function
    '''
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


def Tuplify_LblIdDef( result_bindings ):
    '''
    Function to store additional annotation infos (id and definition) together 
     with a term's label if available from sparql query answer.
    
    result_bindings: content from ["results"]["bindings"] in data structure 
     returned by getData function, i.e. result of sparql query convert with 
     setReturnFormat as JSON.
    
    tupl: ("term label", "term ID", "term definition")
    '''
    lbl, idt, dfn = "", "", ""
    tupl = (lbl, idt, dfn)
    
    if 'label' in result_bindings.keys() and 'value' in result_bindings['label']: lbl = result_bindings['label']['value']
    if 'id'    in result_bindings.keys() and 'value' in result_bindings['id']:    idt = result_bindings[ 'id'  ]['value']
    if 'definition' in result_bindings.keys() and 'value' in result_bindings['definition']: dfn = result_bindings['definition']['value']                
    
    tupl = (lbl,idt,dfn)    
    return tupl


def encodeForWriting( charstr ):
    '''
    Function for compatibility with csv.DictWriter writerow function, which
     can only handle characters included in the ascii space.
    
    charstr: unicode or other formatted string.
    
    returns string ascii formatted with xmlcharrefreplace option
    '''
    out = u"%s".encode('utf-8') %charstr
    return out.encode('ascii', 'xmlcharrefreplace')


def splitTermID( heidy ):
    '''
    Function to return a split-up version of the provided ontology class 
     identifier, in a tuple with everything up to the last hyphen or coma as 
     1st element, and everything following the last hyphen or coma as 2nd element.
        
    heidy: provided ontology class identifier.
    
    '''
    heidy = str(heidy)
    for k in range(1,len(heidy)):    
        if heidy[-k] not in [i for j in (str(range(10)), "_", ":") for i in j]:
            break
    for nx in range(k-1):
        if heidy[-(k-1)+nx] in str(range(10)):
            break
    #print heidy[-(k-1)+nx]    
    return [heidy[:len(heidy)-(k-1)], heidy[-(k-1)+nx:]]


def avoidSpecials( charstr ):
    '''
    Function to return a version of the provdided string with characters that
     can be problematic for some uses replaced by some suite of less
     problematic ones.
    
    http://courses.ischool.berkeley.edu/i290-14/s05/lecture-2/allslides.html
    #26
    '''
    convdict = { "&":"&amp;"  ,\
                 "<":"&lt;"   ,\
                 ">":"&gt;"   ,\
                 "'":"&apos;" ,\
                 '"':"&quot;"  }
    for spec in convdict.keys(): charstr = charstr.replace(spec,convdict[spec])
    return charstr