#'read anchor data from XML file and apply to UFO'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.1.0'

from silfont.genlib import execute
from silfont.UFOlib import *
from xml.etree import ElementTree as ET

argspec = [
    ('ifont',{'help': 'Input UFO'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output UFO','nargs': '?' }, {'type': 'outfont', 'def': '_out'}),
    ('-i','--anchorinfo',{'help': 'XML file with anchor data'}, {'type': 'infile', 'def': '_anc.xml'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_anc.log'}),
    ('-v','--version',{'help': 'UFO version to output'},{}),
    ('-a','--analysis',{'help': 'Analysis only; no output font generated', 'action': 'store_true'},{}),
    # 'choices' for -r should correspond to infont.logger.loglevels.keys()
    ('-r','--report',{'help': 'Set reporting level for log', 'type':str, 'choices':['X','S','E','P','W','I','V']},{}),
    ('-p','--params',{'help': 'Font output parameters','action': 'append'}, {'type': 'optiondict'})
    ]

def doit(args) :
    infont = args.ifont
    r = args.report
    if r: infont.logger.loglevel = infont.logger.loglevels[r]
    glyphcount = 0
    for g in ET.parse(args.anchorinfo).getroot().findall('glyph'):
        glyphcount += 1
        gname = g.get('PSName')
        if gname not in infont.deflayer.keys():
            infont.logger.log("glyph element number " + glyphcount + ": " + gname + " not in font, so skipping anchor data", "W")
            continue
        # anchors currently in font for this glyph
        glyph = infont.deflayer[gname]
        anchorsinfont = set([ ( a.element.get('name'),a.element.get('x'),a.element.get('y') ) for a in glyph['anchor']])
        # anchors in XML file to be added
        anchorstoadd = set()
        for p in g.findall('point'):
            name = p.get('type')
            x = p[0].get('x')               # assume subelement location is first child
            y = p[0].get('y')
            if name and x and y:
                anchorstoadd.add( (name,x,y) )
            else:
                infont.logger.log("Incomplete information for anchor '" + name + "' for glyph " + gname, "E")
        # compare sets
        if anchorstoadd == anchorsinfont:
            if len(anchorstoadd) > 0:
                infont.logger.log("Anchors in file already in font for glyph " + gname + ": " + str(anchorstoadd), "V")
            else:
                infont.logger.log("No anchors in file or in font for glyph " + gname, "V")
        else:
            infont.logger.log("Anchors in file for glyph " + gname + ": " + str(anchorstoadd), "I")
            infont.logger.log("Anchors in font for glyph " + gname + ": " + str(anchorsinfont), "I")
            for name,x,y in anchorstoadd:
                # if anchor being added exists in font already, delete it first
                ancnames = [ i[0] for i in anchorsinfont ]
                if name in ancnames: glyph.remove('anchor', ancnames.index(name))
                glyph.add('anchor', {'name': name, 'x': x, 'y': y})

    # If analysis only, return without writing output font
    if args.analysis: return
    # Return changed font and let execute() write it out
    return infont
    
execute("PSFU", doit, argspec)
