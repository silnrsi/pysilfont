#!/usr/bin/env python
from __future__ import unicode_literals
__doc__ = 'convert composite definition file from XML format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

from silfont.core import execute
from silfont.comp import CompGlyph
from xml.etree import ElementTree as ET

# specify two parameters: input file (XML format), output file (single line format).
argspec = [
    ('input',{'help': 'Input file of CD in XML format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file of CD in single line format'}, {'type': 'outfile'}),
    ('-l', '--log', {'help': 'Optional log file'}, {'type': 'outfile', 'def': '_xml2compdef.log', 'optlog': True})]

def doit(args) :
    cgobj = CompGlyph()
    glyphcount = 0
    for g in ET.parse(args.input).getroot().findall('glyph'):
        glyphcount += 1
        cgobj.CDelement = g
        cgobj.CDline = None
        cgobj.parsefromCDelement()
        if cgobj.CDline != None:
            args.output.write(cgobj.CDline+'\n')
        else:
            pass # error in glyph number glyphcount message
    return
    
def cmd() : execute(None,doit,argspec) 
if __name__ == "__main__": cmd()
