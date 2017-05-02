#!/usr/bin/env python
'export anchor data from UFO to XML file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015,2016 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

from silfont.core import execute
from silfont.etutil import ETWriter
from xml.etree import ElementTree as ET  ### NB: using cElementTree gives bad results

argspec = [
    ('ifont',{'help': 'Input UFO'}, {'type': 'infont'}),
    ('output',{'help': 'Output file exported anchor data in XML format', 'nargs': '?'}, {'type': 'outfile', 'def': '_anc.xml'}),
    ('-g','--gid',{'help': 'Include GID attribute in <glyph> elements', 'action': 'store_true'},{}),
    ('-s','--sort',{'help': 'Sort by PSName attribute in <glyph> elements', 'action': 'store_true'},{}),
    ('-u','--Uprefix',{'help': 'Include U+ prefix on UID attribute in <glyph> elements', 'action': 'store_true'},{}),
    ('-p','--params',{'help': 'XML formatting parameters: indentFirst, indentIncr, attOrder','action': 'append'}, {'type': 'optiondict'})
    ]

def doit(args) :
    infont = args.ifont
    prefix = "U+" if args.Uprefix else ""

    fontElement= ET.Element('font', upem=infont.fontinfo['unitsPerEm'][1].text, name=infont.fontinfo['postscriptFontName'][1].text)
    listorder = []
    for i, e in enumerate(infont.lib['public.glyphOrder'][1]):
        listorder.append( (e.text, i) )
    if args.sort: listorder.sort()

    for g, i in listorder:
        attrib = {'PSName': g}
        if args.gid: attrib['GID'] = str(i)
        u = infont.deflayer[g]['unicode']
        if len(u)>0: attrib['UID'] = prefix + u[0].element.get('hex')
        glyphElement = ET.SubElement(fontElement, 'glyph', attrib)
        anchorlist = []
        for a in infont.deflayer[g]['anchor']:
            anchorlist.append( (a.element.get('name'), a.element.get('x'), a.element.get('y') ) )
        anchorlist.sort()
        for a, x, y in anchorlist:
            anchorElement = ET.SubElement(glyphElement, 'point', attrib = {'type': a})
            locationElement = ET.SubElement(anchorElement, 'location', attrib = {'x': x, 'y': y})

#   instead of simple serialization with: ofile.write(ET.tostring(fontElement))
#   create ETWriter object and specify indentation and attribute order to get normalized output
    ofile = args.output
    indentFirst = ""
    indentIncr = "  "
    attOrder = "name,upem,PSName,GID,UID,type,x,y"
    for k in args.params:
        if k == 'indentIncr': indentIncr = args.params['indentIncr']
        elif k == 'indentFirst': indentFirst = args.params['indentFirst']
        elif k == 'attOrder': attOrder = args.params['attOrder']
    x = attOrder.split(',')
    attributeOrder = dict(zip(x,range(len(x))))
    etwobj=ETWriter(fontElement, indentFirst=indentFirst, indentIncr=indentIncr, attributeOrder=attributeOrder)
    etwobj.serialize_xml(ofile.write)

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
