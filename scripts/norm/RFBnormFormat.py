#!/usr/bin/env python 
'''Normalise the formatting of UFO fonts, primarily based on RoboFab's defaults'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': '_normF'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'normFormat.log'})]

def doit(args) :
    font=args.ifont
    logf = args.log
        
    # Currently no formatting changes identified other than those made by round-tripping through RoboFab
    
    logf.close()
    return font

execute("RFB",doit, argspec)
