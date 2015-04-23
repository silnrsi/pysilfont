#!/usr/bin/python
'''DEPRACATED Module to wrap a Fontforge or Robofab python script. Handles commandline attribute parsing, font 
and file opening (including error handling) etc.
The module pulls attribute strings from the calling module to help it.

DEPRACATED Scripts should now use the execute function from the genlib library
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'
__version__ = '0.0.2'

import sys, argparse, os

def execute(tool, fn, argspec) :
    ff = False
    rfb = False
    if tool == "FF" :
        ff=True
        import fontforge
        if fontforge.hasUserInterface() :
            return # Exceute is for command-line use
    elif tool == "RFB" :
        rfb = True
        from robofab.world import *
    else : return # Invalid tool     
    
    basemodule = sys.modules[fn.__module__]
    poptions = {}
    poptions['description'] = basemodule.__doc__
    if hasattr(basemodule, '__version__') : poptions['epilog'] = "Version: " + basemodule.__version__

    parser = argparse.ArgumentParser(**poptions)

# Process the supplied argument specs, add args to parser, store other info in arginfo
    arginfo = []
    for c,a in enumerate(argspec) :
        # Process all but last tuple entry as argparse arguments
        nonkwds = a[:-2]
        kwds = a[-2]
        parser.add_argument(*nonkwds, **kwds)
        # Create dict of framework keywords using argument name
        argn = nonkwds[-1] # Find the argument name from first 1 or 2 tuple entries
        if argn[0:2] == "--" : argn = argn[2:] # Will start with -- for options
        ainfo=fkwds=a[-1]
        ainfo['name']=argn
        arginfo.append(ainfo)

# Parse the command-line arguments. If errors or -h used, procedure will exit here
    args = parser.parse_args()

# Process the argument values returned from argparse
    (fppath,fpbase,fpext)=_splitfn(getattr(args,arginfo[0]['name'])) # First pos param use for defaulting
    outfont = None
    
    for c,ainfo in enumerate(arginfo) :
        aval = getattr(args,ainfo['name'])
        atype = ainfo['type'] if 'type' in ainfo else None
        adef = ainfo['def'] if 'def' in ainfo else None
        if c <> 0 : #Handle defaults for all but first positional parameter
            if adef :
                if not aval : aval=""               
                (apath,abase,aext)=_splitfn(aval)
                (dpath,dbase,dext)=_splitfn(adef) # dbase should be None
                if not apath : apath=fppath
                if not abase : abase = fpbase + dbase
                if not aext :
                    if dext :
                        aext = dext
                    elif (atype=='outfont' or atype=='infont') : aext = fpext
                aval = os.path.join(apath,abase+aext)
        # Open files/fonts
        if atype=='infont' :
            print 'Opening font: ',aval
            try :
                if ff : aval=fontforge.open(aval)
                if rfb: aval=OpenFont(aval)
            except Exception as e :
                print e
                sys.exit()
        elif atype=='infile' :
            print 'Opening file for input: ',aval
            try :
                aval=open(aval,"r")
            except Exception as e :
                print e
                sys.exit()
        elif atype=='outfile' :
            print 'Opening file for output: ',aval
            try :
                aval=open(aval,"w")
            except Exception as e :
                print e
                sys.exit()
        elif atype=='outfont' : 
            outfont=aval # Can only be one outfont
            outfontext=aext
        
        setattr(args,ainfo['name'],aval)

# All arguments processed, now call the main function
    result = fn(args)
    if outfont :
        if result is None :
            print "No font output"
        else :
            print "Saving font to " + outfont
            if outfontext=="ufo" and ff:
                result.generate(outfont)
            else : result.save(outfont)

def _splitfn(fn): # Split filename into path, base and extension
    (path,base) = os.path.split(fn)
    (base,ext) = os.path.splitext(base)
    return (path,base,ext)
