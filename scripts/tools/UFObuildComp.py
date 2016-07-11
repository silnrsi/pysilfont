#!/usr/bin/env python
'''Read Composite Definitions and add gylphs to a UFO font'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

from xml.etree import cElementTree as ET
from silfont.core import execute
import silfont.ufo.ufo as ufo
from silfont.comp.comp import CompGlyph

argspec = [
    ('ifont',{'help': 'Input UFO'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output UFO','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--cdfile',{'help': 'Composite Definitions input file'}, {'type': 'infile', 'def': '_CD.txt'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_CD.log'}),
    ('-a','--analysis',{'help': 'Analysis only; no output font generated', 'action': 'store_true'},{}),
    ('-f','--force',{'help': 'Force overwrite of glyphs having outlines', 'action': 'store_true'},{}),
     # 'choices' for -r should correspond to infont.logger.loglevels.keys() ### -r may move to core.py eventually
    ('-r','--report',{'help': 'Set reporting level for log', 'type':str, 'choices':['X','S','E','P','W','I','V']},{})
    ]

glyphlist = []  # accessed as global by recursive function addtolist() and main function doit()

def addtolist(e, prevglyph):
    """Given an element ('base' or 'attach') and the name of previous glyph,
    add a tuple to the list of glyphs in this composite, including
    "at" and "with" attachment point information, and x and y shift values
    """
    global glyphlist
    subelementlist = []
    thisglyphname = e.get('PSName')
    atvalue = e.get("at")
    withvalue = e.get("with")
    shiftx = shifty = None
    for se in e:
        if se.tag == 'property': pass
        elif se.tag == 'shift':
            shiftx = se.get('x')
            shifty = se.get('y')
        elif se.tag == 'attach':
            subelementlist.append( se )
    glyphlist.append( ( thisglyphname, prevglyph, atvalue, withvalue, shiftx, shifty ) )
    for se in subelementlist:
        addtolist(se, thisglyphname)

def addtwo(a1, a2):
    """Take two items (string, number or None), convert to integer and return sum"""
    b1 = int(a1) if a1 is not None else 0
    b2 = int(a2) if a2 is not None else 0
    return b1 + b2

def doit(args) :
    global glyphlist
    infont = args.ifont
    if args.report: infont.logger.loglevel = args.report

    ### temp section (these may someday be passed as optional parameters)
    RemoveUsedAnchors = True
    FlattenComponents = True
    ### end of temp section

    cgobj = CompGlyph()

    for linenum, rawCDline in enumerate(args.cdfile):
        CDline=rawCDline.strip()
        if len(CDline) == 0 or CDline[0] == "#": continue
        infont.logger.log("Processing line " + str(linenum+1) + ": " + CDline,"I")
        cgobj.CDline=CDline
        try:
            cgobj.parsefromCDline()
        except ValueError as mess:
            infont.logger.log("Parsing error: " + str(mess), "E")
            continue
        g = cgobj.CDelement

        # Collect target glyph information and construct list of component glyphs
        targetglyphname = g.get("PSName")
        targetglyphunicode = g.get("UID")
        glyphlist = []	# list of component glyphs
        lsb = rsb = 0
        adv = None
        for e in g:
            if e.tag == 'note': pass
            elif e.tag == 'property': pass	# ignore mark info
            elif e.tag == 'lsb': lsb = int(e.get('width'))
            elif e.tag == 'rsb': rsb = int(e.get('width'))
            elif e.tag == 'advance': adv = int(e.get('width'))
            elif e.tag == 'base':
                addtolist(e,None)
        infont.logger.log(str(glyphlist),"V")

        # find each component glyph and compute x,y position
        xbase = xadvance = lsb
        ybase = 0
        componentlist = []
        targetglyphanchors = {} # dictionary of {name: (xOffset,yOffset)}
        for currglyph, prevglyph, baseAP, diacAP, shiftx, shifty in glyphlist:
            # get current glyph and its anchor names from font
            if currglyph not in infont.deflayer:
                infont.logger.log(currglyph + " not found in font", "E")
                continue
            cg = infont.deflayer[currglyph]
            cganc = [x.element.get('name') for x in cg['anchor']]
            diacAPx = diacAPy = 0
            baseAPx = baseAPy = 0
            if prevglyph is None:   # this is new 'base'
                xbase = xadvance
                xOffset = xbase
                yOffset = 0
            else:                 	# this is 'attach'
                if diacAP is not None: # find diacritic Attachment Point in currglyph
                    if diacAP not in cganc:
                        infont.logger.log("The AP '" + diacAP + "' does not exist on diacritic glyph " + currglyph, "E")
                    else:
                        i = cganc.index(diacAP)
                        diacAPx = int(cg['anchor'][i].element.get('x'))
                        diacAPy = int(cg['anchor'][i].element.get('y'))
                else:
                    infont.logger.log("No AP specified for diacritic " + currglyph, "E")
                if baseAP is not None: # find base character Attachment Point in targetglyph
                    if baseAP not in targetglyphanchors.keys():
                        infont.logger.log("The AP '" + baseAP + "' does not exist on base glyph when building " + targetglyphname, "E")
                    else:
                        baseAPx = targetglyphanchors[baseAP][0]
                        baseAPy = targetglyphanchors[baseAP][1]
                        if RemoveUsedAnchors:
                            infont.logger.log("Removing used anchor " + baseAP, "V")
                            del targetglyphanchors[baseAP]
                xOffset = baseAPx - diacAPx
                yOffset = baseAPy - diacAPy

            if shiftx is not None: xOffset += int(shiftx)
            if shifty is not None: yOffset += int(shifty)

            componentdic = {'base': currglyph}
            if xOffset != 0: componentdic['xOffset'] = str(xOffset)
            if yOffset != 0: componentdic['yOffset'] = str(yOffset)
            componentlist.append( componentdic )

            # Find advance width of currglyph and add to xadvance
            xadvance += int(cg['advance'].element.get('width'))

            # Move anchor information to targetglyphanchors
            for a in cg['anchor']:
                dic = a.element.attrib
                thisanchorname = dic['name']
                if RemoveUsedAnchors and thisanchorname == diacAP:
                    infont.logger.log("Skiping used anchor " + diacAP, "V")
                    continue # skip this anchor
                # add anchor (adjusted for position in targetglyph)
                targetglyphanchors[thisanchorname] = ( int( dic['x'] ) + xOffset, int( dic['y'] ) + yOffset )
                infont.logger.log("Adding anchor " + thisanchorname + ": " + str(targetglyphanchors[thisanchorname]), "V")
            infont.logger.log(str(targetglyphanchors),"V")

        xbase = xadvance + rsb ### adjust with rsb
        if adv is not None: xbase = adv ### if adv specified, then this advance value overrides calculated value

        infont.logger.log("Glyph: " + targetglyphname + ", " + str(targetglyphunicode) + ", " + str(xbase), "V")
        for c in componentlist:
            infont.logger.log(str(c), "V")

        # Flatten components
        if FlattenComponents:
            newcomponentlist = []
            for compdic in componentlist:
                c = compdic['base']
                x = compdic.get('xOffset')
                y = compdic.get('yOffset')
                # look up component glyph
                g=infont.deflayer[c]
                # check if it has only components (that is, no contours) in outline
                if g['outline'] and g['outline'].components and not g['outline'].contours:
                    # for each component, get base, x1, y1 and create new entry with base, x+x1, y+y1
                    for subcomp in g['outline'].components:
                        b = subcomp.element.get('base')
                        x1 = subcomp.element.get('xOffset')
                        y1 = subcomp.element.get('yOffset')
                        xOffset = addtwo(x, x1)
                        yOffset = addtwo(y, y1)
                        componentdic = {'base': b}
                        if xOffset != 0: componentdic['xOffset'] = str(xOffset)
                        if yOffset != 0: componentdic['yOffset'] = str(yOffset)
                        newcomponentlist.append( componentdic )
                else:
                    newcomponentlist.append( compdic )
            if componentlist == newcomponentlist:
                infont.logger.log("No changes to flatten components", "V")
            else:
                componentlist = newcomponentlist
                infont.logger.log("Components flattened", "V")
                for c in componentlist:
                    infont.logger.log(str(c), "V")

        # Check if this new glyph exists in the font already; if so, decide whether to replace, or issue warning
        if  targetglyphname in infont.deflayer.keys():
            infont.logger.log("Target glyph, " + targetglyphname + ", already exists in font.", "V")
            g = infont.deflayer[targetglyphname]
            if g['outline'] and g['outline'].contours and not args.force: # don't replace glyph with contours, unless -f set
                infont.logger.log("Not replacing existing glyph, " + targetglyphname + ", because it has contours.", "W")
                continue
            else:
                infont.logger.log("Replacing glyph, " + targetglyphname, "V")
                infont.deflayer.delGlyph(targetglyphname) ### delete existing glyph
        else:
            infont.logger.log("Adding new glyph, " + targetglyphname, "V")

        # create glyph, using targetglyphname, targetglyphunicode
        targetglyph = ufo.Uglif(layer=infont.deflayer, name=targetglyphname)
        targetglyph.add('advance',{'width': str(xbase)} )
        if targetglyphunicode: targetglyph.add('unicode',{'hex': targetglyphunicode} )
        targetglyph.add('outline')
        # add to the outline element, a component element for every entry in componentlist
        for compdic in componentlist:
            comp = ufo.Ucomponent(targetglyph['outline'],ET.Element('component',compdic))
            targetglyph['outline'].appendobject(comp,'component')
        # copy anchors to new glyph from targetglyphanchors which has {'U': (500,1000), 'L': (500,0)}
        for a in targetglyphanchors:
            targetglyph.add('anchor', {'name': a, 'x': str(targetglyphanchors[a][0]), 'y': str(targetglyphanchors[a][1])} )
        # actually add the glyph to the font
        infont.deflayer.addGlyph(targetglyph)

    # If analysis only, return without writing output font
    if args.analysis: return
    # Return changed font and let execute() write it out
    return infont

execute("PSFU", doit, argspec)
