#!/usr/bin/env python
"""
This script builds the python documentation from the function signature and the
".pod" files that document the Fortran library. The processed documentation is
saved as ascii text files which are loaded on runtime and replace the __doc__
string of the f2py wrapped functions.
"""

import sys, os, re
import _SHTOOLS
import mydebug

def main():
    #---- input/output folders ----
    libfolder = os.path.abspath(sys.argv[1])
    poddocfolder = os.path.join(libfolder,'src/doc')
    pydocfolder = os.path.join(libfolder,'pyshtools/doc')
    print '---- searching documentation in folder: {} ----'.format(poddocfolder)
    
    #---- pod file search patterns ----
    redescr = re.compile('DESCRIPTION(.*?)=head1 ARGUMENTS',re.DOTALL)
    renotes = re.compile('NOTES(.*?)=head1',re.DOTALL)

    #---- loop through the f2py _SHTOOLS functions and make docstrings ----
    for name,func in _SHTOOLS.__dict__.items():
        if callable(func):
            try:
                #-- process and load documentation from different sources --
                #get and process f2py generated call signature:
                callsign = process_f2pydoc(func.__doc__)
                signature = 'SIGNATURE\n---------\n' + callsign
    
                #read pod file documentation:
                fname_poddoc = os.path.join(poddocfolder,name.lower()+'.pod')
                podfile   = open(fname_poddoc,'r')
                podstring = podfile.read()
    
                match = redescr.search(podstring)
                if match is None:
                    description = '\nDESCRIPTION\n-----------\nDOCUMENTATION NOT AVAILABLE'
                else:
                    description = '\nDESCRIPTION\n-----------' + match.group(1)
    
                match = renotes.search(podstring)
                if match is None:
                    notes       = ''
                else:
                    notes       = '\nNOTES\n-----'+ match.group(1)
    
                podfile.close()
    
                #combine docstring:
                docstring       =  signature + description + notes
    
                #-- save combined docstring in the pydoc folder--
                fname_pydoc  = os.path.join( pydocfolder,name.lower()+'.doc')
                pydocfile = open(fname_pydoc,'w')
                pydocfile.write(docstring)
                pydocfile.close()
    
            except IOError,msg:
                print msg

#===== HELPER FUNCTIONS ====
def process_f2pydoc(f2pydoc):
    """
    this function replace all optional _d0 arguments with their default values
    in the function signature. These arguments are not intended to be used and
    signify merely the array dimensions of the associated argument.
    """
    #---- split f2py document in its parts
    #0=Call Signature
    #1=Parameters
    #2=Other (optional) Parameters (only if present)
    #3=Returns
    docparts    = re.split('\n--',f2pydoc)

    if len(docparts) == 4: 
        doc_has_optionals = True
    elif len(docparts) == 3:
        doc_has_optionals = False
    else:
        print '-- uninterpretable f2py documentation --'
        return f2pydoc

    #---- replace arguments with _d suffix with empty string in function signature (remove them):
    docparts[0] = re.sub('[\[(,]\w+_d\d','',docparts[0])

    #---- replace _d arguments of the return arrays with their default value:
    if doc_has_optionals:

        returnarray_dims = re.findall('[\[(,](\w+_d\d)',docparts[3])
        for arg in returnarray_dims:
            searchpattern = arg+' : input.*\n.*Default: (.*)\n'
            match = re.search(searchpattern,docparts[2])
            if match:
                default = match.group(1) #this returns the value in brackets in the search pattern
                docparts[3] = re.sub(arg,default,docparts[3])

    #---- combine doc parts to a single string
    processed_signature = '\n--'.join(docparts)

    return processed_signature

#==== EXECUTE SCRIPT ====
if __name__ == "__main__":
    main()
