#'convert composite definition file to XML format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.4'

from silfont.genlib import execute
from silfont.genlib import ETWriter
from silfont.composites import CompGlyph
from xml.etree import ElementTree as ET

# specify three parameters: input file (single line format), output file (XML format), log file.
argspec = [
    ('input',{'help': 'Input file of CD in single line format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file of CD in XML format'}, {'type': 'outfile', 'def': '_out.xml'}),
    ('log',{'help': 'Log file'},{'type': 'outfile', 'def': '_log.txt'})]

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
    etwobj=ETWriter(f, indentFirst='   ', indentIncr='   ', attributeOrder={'PSName':0,'UID':1,'with':2,'at':3,'x':4,'y':5})
    etwobj.serialize_xml(ofile.write)
    
    return
    
execute(None,doit,argspec)
