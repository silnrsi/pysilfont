#!/usr/bin/env python
'convert composite definition file to XML format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.2.0'

from silfont.genlib import execute
from silfont.genlib import ETWriter
from silfont.complib import CompGlyph
from xml.etree import ElementTree as ET

# specify three parameters: input file (single line format), output file (XML format), log file
# and optional -p indentFirst "   " -p indentIncr "   " -p "PSName,UID,with,at,x,y" for XML formatting.
argspec = [
    ('input',{'help': 'Input file of CD in single line format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file of CD in XML format'}, {'type': 'outfile', 'def': '_out.xml'}),
    ('log',{'help': 'Log file'},{'type': 'outfile', 'def': '_log.txt'}),
    ('-p','--params',{'help': 'XML formatting parameters: indentFirst, indentIncr, attOrder','action': 'append'}, {'type': 'optiondict'})]

def doit(args) :
    ofile = args.output
    lfile = args.log
    filelinecount = 0
    linecount = 0
    elementcount = 0
    cgobj = CompGlyph()
    f = ET.Element('font')
    for line in args.input.readlines():
        filelinecount += 1
        testline = line.strip()
	if len(testline) > 0 and testline[0] != '#':  # not whitespace or comment
            linecount += 1
            cgobj.CDline=line
            cgobj.CDelement=None
            try:
                cgobj.parsefromCDline()
                if cgobj.CDelement != None:
                    f.append(cgobj.CDelement)
                    elementcount += 1
            except ValueError, e:
                lfile.write("Line "+str(filelinecount)+": "+str(e)+'\n')
    if linecount != elementcount:
        lfile.write("Lines read from input file: " + str(filelinecount)+'\n')
        lfile.write("Lines parsed (excluding blank and comment lines): " + str(linecount)+'\n')
        lfile.write("Valid glyphs found: " + str(elementcount)+'\n')
#   instead of simple serialization with: ofile.write(ET.tostring(f))
#   create ETWriter object and specify indentation and attribute order to get normalized output
    indentFirst = "   "
    indentIncr = "   "
    attOrder = "PSName,UID,with,at,x,y"
    for k in args.params:
        if k == 'indentIncr': indentIncr = args.params['indentIncr']
        elif k == 'indentFirst': indentFirst = args.params['indentFirst']
        elif k == 'attOrder': attOrder = args.params['attOrder']
    x = attOrder.split(',')
    attributeOrder = dict(zip(x,range(len(x))))
    etwobj=ETWriter(f, indentFirst=indentFirst, indentIncr=indentIncr, attributeOrder=attributeOrder)
    etwobj.serialize_xml(ofile.write)
    
    return
    
execute(None,doit,argspec)
