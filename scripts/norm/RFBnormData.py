#!/usr/bin/env python 
'''Normalise data in UFO fonts to allow for changes made by other tools'''
__url__ = 'http://projects.palaso.org/projects/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': '_normD'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'normData.log'})]

def doit(args) :
    font=args.ifont
    logf = args.log
        
    # Create pointers to main objects
    finfo=font.info
    flib=font.lib
    
    # Glyphs changes .null to null so change back
    if font.has_key("null"):
        logf.write ("null glyph name changed to .null\n")
        font["null"].name=".null"

    # Read saved info from lib
    nfikey="org.sil.normSavedFontinfo"
    if nfikey in flib:
        savedfi=flib[nfikey]
    else: savedfi={}
    
    # Process changes in fontinfo.plist using previous copy saved in lib
    for key in savedfi:
        if not(key in finfo.__dict__):
            finfo.__dict__[key]=savedfi[key]
            logf.write (key + " added back into fontinfo.plist with value: " + str(savedfi[key]) + "\n")
    # Save current fontinfo values in lib for future normalisation runs
    fidict=dict(finfo.__dict__) # Create new dictionary with current fontinfo values
    del fidict['_object'] # Remove non-key attributes from dict
    del fidict['changed']
    del fidict['getParent']
    del fidict['selected']
    flib[nfikey]=fidict
    
    logf.close()
    return font

execute("RFB",doit, argspec)
