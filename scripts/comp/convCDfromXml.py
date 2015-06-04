#'convert composite definition file from XML format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.4'

from silfont.genlib import execute
from silfont.composites import CompGlyph
from xml.etree import ElementTree as ET

# specify two parameters: input file (XML format), output file (single line format).
argspec = [
    ('input',{'help': 'Input file of CD in XML format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file of CD in single line format'}, {'type': 'outfile'})]

def doit(args) :
#    for g in ET.parse(args.input).getroot().findall('glyph'):
    doctree = ET.parse(args.input)
    docroot = doctree.getroot()
    cgobj = CompGlyph()
    for g in docroot.findall('glyph'):
        cgobj.CDelement = g
        cgobj.CDline = None
        cgobj.parsefromCDelement()
        if cgobj.CDline != None:
            args.output.write(cgobj.CDline+'\n')
    return
    
execute(None,doit,argspec)
