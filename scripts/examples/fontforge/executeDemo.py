#!/usr/bin/env python
'Demo using execute() with no font tool'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.genlib import *

argspec = [
    ('input',{'help': 'Input file'}, {'type': 'infile'}),
    ('output',{'help': 'Output file','nargs': '?' }, {'type': 'outfile', 'def': '_out.txt'})]

def doit(args) :
    infile = args.input
    outfile = args.output
    
    for line in infile:
        outfile.write(line)
    
    outfile.close()
    
    return
    
execute("",doit,argspec) # Could also use None for the tool