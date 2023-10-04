#!/usr/bin/env python3
__doc__ = 'export anchor data from UFO to XML file'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015,2016 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

from silfont.core import execute
from silfont.etutil import ETWriter
from xml.etree import ElementTree as ET

argspec = [
    ('ifont',{'help': 'Input UFO'}, {'type': 'infont'}),
    ('output',{'help': 'Output file exported anchor data in XML format', 'nargs': '?'}, {'type': 'outfile', 'def': '_anc.xml'}),
    ('-r','--report',{'help': 'Set reporting level for log', 'type':str, 'choices':['X','S','E','P','W','I','V']},{}),
    ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': '_anc.log'}),
    ('-g','--gid',{'help': 'Include GID attribute in <glyph> elements', 'action': 'store_true'},{}),
    ('-s','--sort',{'help': 'Sort by public.glyphOrder in lib.plist', 'action': 'store_true'},{}),
    ('-u','--Uprefix',{'help': 'Include U+ prefix on UID attribute in <glyph> elements', 'action': 'store_true'},{}),
    ('-p','--params',{'help': 'XML formatting parameters: indentFirst, indentIncr, attOrder','action': 'append'}, {'type': 'optiondict'})
    ]

def doit(args) :
    logfile = args.logger
    if args.report: logfile.loglevel = args.report
    infont = args.ifont
    prefix = "U+" if args.Uprefix else ""

    if hasattr(infont, 'lib') and 'public.glyphOrder' in infont.lib:
        glyphorderlist = [s.text for s in infont.lib['public.glyphOrder'][1].findall('string')]
    else:
        glyphorderlist = []
        if args.gid:
            logfile.log("public.glyphOrder is absent; ignoring --gid option", "E")
            args.gid = False
    glyphorderset = set(glyphorderlist)
    if len(glyphorderlist) != len(glyphorderset):
        logfile.log("At least one duplicate name in public.glyphOrder", "W")
        # count of duplicate names is len(glyphorderlist) - len(glyphorderset)
    actualglyphlist = [g for g in infont.deflayer.keys()]
    actualglyphset = set(actualglyphlist)
    listorder = []
    gid = 0
    for g in glyphorderlist:
        if g in actualglyphset:
            listorder.append( (g, gid) )
            gid += 1
            actualglyphset.remove(g)
            glyphorderset.remove(g)
        else:
            logfile.log(g + " in public.glyphOrder list but absent from UFO", "W")
    if args.sort: listorder.sort()
    for g in sorted(actualglyphset):    # if any glyphs remaining
        listorder.append( (g, None) )
        logfile.log(g + " in UFO but not in public.glyphOrder list", "W")

    if 'postscriptFontName' in infont.fontinfo:
        postscriptFontName = infont.fontinfo['postscriptFontName'][1].text
    else:
        if 'styleMapFamilyName' in infont.fontinfo:
            family = infont.fontinfo['styleMapFamilyName'][1].text
        elif 'familyName' in infont.fontinfo:
            family = infont.fontinfo['familyName'][1].text
        else:
            family = "UnknownFamily"
        if 'styleMapStyleName' in infont.fontinfo:
            style = infont.fontinfo['styleMapStyleName'][1].text.capitalize()
        elif 'styleName' in infont.fontinfo:
            style = infont.fontinfo['styleName'][1].text
        else:
            style = "UnknownStyle"

        postscriptFontName = '-'.join((family,style)).replace(' ','')
    fontElement= ET.Element('font', upem=infont.fontinfo['unitsPerEm'][1].text, name=postscriptFontName)
    for g, i in listorder:
        attrib = {'PSName': g}
        if args.gid and i != None: attrib['GID'] = str(i)
        u = infont.deflayer[g]['unicode']
        if len(u)>0: attrib['UID'] = prefix + u[0].element.get('hex')
        glyphElement = ET.SubElement(fontElement, 'glyph', attrib)
        anchorlist = []
        for a in infont.deflayer[g]['anchor']:
            anchorlist.append( (a.element.get('name'), int(float(a.element.get('x'))), int(float(a.element.get('y'))) ) )
        anchorlist.sort()
        for a, x, y in anchorlist:
            anchorElement = ET.SubElement(glyphElement, 'point', attrib = {'type': a})
            locationElement = ET.SubElement(anchorElement, 'location', attrib = {'x': str(x), 'y': str(y)})

#   instead of simple serialization with: ofile.write(ET.tostring(fontElement))
#   create ETWriter object and specify indentation and attribute order to get normalized output
    ofile = args.output
    indentFirst = args.params.get('indentFirst', "")
    indentIncr = args.params.get('indentIncr', "  ")
    attOrder = args.params.get('attOrder', "name,upem,PSName,GID,UID,type,x,y")
    x = attOrder.split(',')
    attributeOrder = dict(zip(x,range(len(x))))
    etwobj=ETWriter(fontElement, indentFirst=indentFirst, indentIncr=indentIncr, attributeOrder=attributeOrder)
    ofile.write(etwobj.serialize_xml())

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
