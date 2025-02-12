#!/usr/bin/env python3
'Demo script for use of ETWriter'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.etutil as etutil
from xml.etree import cElementTree as ET

argspec = [('outfile1',{'help': 'output file 1','default': './xmlDemo.xml','nargs': '?'}, {'type': 'outfile'}),
            ('outfile2',{'help': 'output file 2','nargs': '?'}, {'type': 'outfile', 'def':'_2.xml'}),
            ('outfile3',{'help': 'output file 3','nargs': '?'}, {'type': 'outfile', 'def':'_3.xml'})]

def doit(args) :
    ofile1 = args.outfile1
    ofile2 = args.outfile2
    ofile3 = args.outfile3

    xmlstring = "<item>\n<subitem hello='world'>\n<subsub name='moon'>\n<value>lunar</value>\n</subsub>\n</subitem>"
    xmlstring += "<subitem hello='jupiter'>\n<subsub name='moon'>\n<value>IO</value>\n</subsub>\n</subitem>\n</item>"

    # Using etutil's xmlitem class
    
    xmlobj = etutil.xmlitem()
    xmlobj.etree = ET.fromstring(xmlstring)
    
    etwobj = etutil.ETWriter(xmlobj.etree)
    xmlobj.outxmlstr = etwobj.serialize_xml()

    ofile1.write(xmlobj.outxmlstr)
    
    # Just using ETWriter
    
    etwobj = etutil.ETWriter( ET.fromstring(xmlstring) )
    xmlstr = etwobj.serialize_xml()
    ofile2.write(xmlstr)
    # Changing parameters
    
    etwobj = etutil.ETWriter( ET.fromstring(xmlstring) )
    etwobj.indentIncr = "    "
    etwobj.indentFirst = ""
    xmlstr = etwobj.serialize_xml()
    ofile3.write(xmlstr)

    # Close files and exit
    ofile1.close()
    ofile2.close()
    ofile3.close()
    return

def cmd() : execute("",doit,argspec) 
if __name__ == "__main__": cmd()
