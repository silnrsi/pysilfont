#'convert composite definition file to XML format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.2'

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
    f = ET.Element('font')
    for line in args.input.readlines():      ### could use enumerate() to get (zero-based) line number to include with errors
        testline = line.strip()
	if len(testline) > 0 and testline[0] != '#':  # not whitespace or comment
            try:
                cgobj = CompGlyph(CDline=line)
                cgobj.parsefromCDline()
                f.append(cgobj.CDelement)
            except ValueError:
                pass # log errors
                #lfile.write(e+'\n')
#   instead of simple serialization with: ofile.write(ET.tostring(f))
#   create ETWriter object and specify indentation and attribute order to get normalized output
    etwobj=ETWriter(f, indentFirst='   ', indentIncr='   ', attributeOrder={'PSName':0,'UID':1,'with':2,'at':3,'x':4,'y':5})
    etwobj.serialize_xml(ofile.write)
    
    return
    
execute(None,doit,argspec)
