#!/usr/bin/env python
__doc__ = '''Read Composite Definitions and add glyphs to a UFO font'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

try:
    xrange
except NameError:
    xrange = range
from xml.etree import ElementTree as ET
import re
from silfont.core import execute
import silfont.ufo as ufo
from silfont.comp import CompGlyph
from silfont.etutil import ETWriter
from silfont.util import parsecolors

argspec = [
    ('ifont',{'help': 'Input UFO'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output UFO','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--cdfile',{'help': 'Composite Definitions input file'}, {'type': 'infile', 'def': '_CD.txt'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_CD.log'}),
    ('-a','--analysis',{'help': 'Analysis only; no output font generated', 'action': 'store_true'},{}),
    ('-c','--color',{'help': 'Color cells of generated glyphs', 'action': 'store_true'},{}),
    ('--colors', {'help': 'Color(s) to use when marking generated glyphs'},{}),
    ('-f','--force',{'help': 'Force overwrite of glyphs having outlines', 'action': 'store_true'},{}),
    ('-n','--noflatten',{'help': 'Do not flatten component references', 'action': 'store_true'},{}),
    ('--remove',{'help': 'a regex matching anchor names that should always be removed from composites'},{}),
    ('--preserve', {'help': 'a regex matching anchor names that, if present in glyphs about to be replace, should not be overwritten'}, {})
    ]

glyphlist = []  # accessed as global by recursive function addtolist() and main function doit()

def doit(args):
    global glyphlist
    infont = args.ifont
    logger = args.logger
    params = infont.outparams

    removeRE = re.compile(args.remove) if args.remove else None
    preserveRE = re.compile(args.preserve) if args.preserve else None

    colors = None
    if args.color or args.colors:
        colors = args.colors if args.colors else "(0.04,0.57,0.04,1')"
        colors = parsecolors(colors)
        invalid = False
        for color in colors:
            if color[0] is None:
                invalid = True
                logger.log(color[2], "E")
        if len(colors) > 3:
            logger.log("A maximum of three colors can be supplied: " + str(len(colors)) + " supplied", "E")
            invalid = True
        if invalid: logger.log("Re-run with valid colors", "S")
        if len(colors) == 1: colors.append(colors[0])
        if len(colors) == 2: colors.append(colors[1])
        logstatuses = ("Glyph unchanged", "Glyph changed", "New glyph")

    ### temp section (these may someday be passed as optional parameters)
    RemoveUsedAnchors = True
    ### end of temp section

    cgobj = CompGlyph()

    for linenum, rawCDline in enumerate(args.cdfile):
        CDline=rawCDline.strip()
        if len(CDline) == 0 or CDline[0] == "#": continue
        logger.log("Processing line " + str(linenum+1) + ": " + CDline,"I")
        cgobj.CDline=CDline
        try:
            cgobj.parsefromCDline()
        except ValueError as mess:
            logger.log("Parsing error: " + str(mess), "E")
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
        logger.log(str(glyphlist),"V")

        # find each component glyph and compute x,y position
        xbase = xadvance = lsb
        ybase = 0
        componentlist = []
        targetglyphanchors = {} # dictionary of {name: (xOffset,yOffset)}
        for currglyph, prevglyph, baseAP, diacAP, shiftx, shifty in glyphlist:
            # get current glyph and its anchor names from font
            if currglyph not in infont.deflayer:
                logger.log(currglyph + " not found in font", "E")
                continue
            cg = infont.deflayer[currglyph]
            cganc = [x.element.get('name') for x in cg['anchor']]
            diacAPx = diacAPy = 0
            baseAPx = baseAPy = 0
            if prevglyph is None:   # this is new 'base'
                xbase = xadvance
                xOffset = xbase
                yOffset = 0
                # Find advance width of currglyph and add to xadvance
                if 'advance' in cg:
                    cgadvance = cg['advance']
                    if cgadvance is not None and cgadvance.element.get('width') is not None:
                        xadvance += int(float(cgadvance.element.get('width')))
            else:                 	# this is 'attach'
                if diacAP is not None: # find diacritic Attachment Point in currglyph
                    if diacAP not in cganc:
                        logger.log("The AP '" + diacAP + "' does not exist on diacritic glyph " + currglyph, "E")
                    else:
                        i = cganc.index(diacAP)
                        diacAPx = int(float(cg['anchor'][i].element.get('x')))
                        diacAPy = int(float(cg['anchor'][i].element.get('y')))
                else:
                    logger.log("No AP specified for diacritic " + currglyph, "E")
                if baseAP is not None: # find base character Attachment Point in targetglyph
                    if baseAP not in targetglyphanchors.keys():
                        logger.log("The AP '" + baseAP + "' does not exist on base glyph when building " + targetglyphname, "E")
                    else:
                        baseAPx = targetglyphanchors[baseAP][0]
                        baseAPy = targetglyphanchors[baseAP][1]
                        if RemoveUsedAnchors:
                            logger.log("Removing used anchor " + baseAP, "V")
                            del targetglyphanchors[baseAP]
                xOffset = baseAPx - diacAPx
                yOffset = baseAPy - diacAPy

            if shiftx is not None: xOffset += int(shiftx)
            if shifty is not None: yOffset += int(shifty)

            componentdic = {'base': currglyph}
            if xOffset != 0: componentdic['xOffset'] = str(xOffset)
            if yOffset != 0: componentdic['yOffset'] = str(yOffset)
            componentlist.append( componentdic )

            # Move anchor information to targetglyphanchors
            for a in cg['anchor']:
                dic = a.element.attrib
                thisanchorname = dic['name']
                if RemoveUsedAnchors and thisanchorname == diacAP:
                    logger.log("Skipping used anchor " + diacAP, "V")
                    continue # skip this anchor
                # add anchor (adjusted for position in targetglyph)
                targetglyphanchors[thisanchorname] = ( int( dic['x'] ) + xOffset, int( dic['y'] ) + yOffset )
                logger.log("Adding anchor " + thisanchorname + ": " + str(targetglyphanchors[thisanchorname]), "V")
            logger.log(str(targetglyphanchors),"V")

        if adv is not None:
            xadvance = adv  ### if adv specified, then this advance value overrides calculated value
        else:
            xadvance += rsb ### adjust with rsb

        logger.log("Glyph: " + targetglyphname + ", " + str(targetglyphunicode) + ", " + str(xadvance), "V")
        for c in componentlist:
            logger.log(str(c), "V")

        # Flatten components unless -n set
        if not args.noflatten:
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
                        componentdic = subcomp.element.attrib.copy()
                        x1 = componentdic.pop('xOffset', 0)
                        y1 = componentdic.pop('yOffset', 0)
                        xOffset = addtwo(x, x1)
                        yOffset = addtwo(y, y1)
                        if xOffset != 0: componentdic['xOffset'] = str(xOffset)
                        if yOffset != 0: componentdic['yOffset'] = str(yOffset)
                        newcomponentlist.append( componentdic )
                else:
                    newcomponentlist.append( compdic )
            if componentlist == newcomponentlist:
                logger.log("No changes to flatten components", "V")
            else:
                componentlist = newcomponentlist
                logger.log("Components flattened", "V")
                for c in componentlist:
                    logger.log(str(c), "V")

        # Check if this new glyph exists in the font already; if so, decide whether to replace, or issue warning
        preservedAPs = set()
        if  targetglyphname in infont.deflayer.keys():
            logger.log("Target glyph, " + targetglyphname + ", already exists in font.", "V")
            targetglyph = infont.deflayer[targetglyphname]
            if targetglyph['outline'] and targetglyph['outline'].contours and not args.force: # don't replace glyph with contours, unless -f set
                logger.log("Not replacing existing glyph, " + targetglyphname + ", because it has contours.", "W")
                continue
            else:
                logger.log("Replacing information in existing glyph, " + targetglyphname, "I")
                glyphstatus = "Replace"
                # delete information from existing glyph
                targetglyph.remove('outline')
                targetglyph.remove('advance')
                for i in xrange(len(targetglyph['anchor'])-1,-1,-1):
                    aname = targetglyph['anchor'][i].element.attrib['name']
                    if preserveRE is not None and preserveRE.match(aname):
                        preservedAPs.add(aname)
                        logger.log("Preserving anchor " + aname, "V")
                    else:
                        targetglyph.remove('anchor',index=i)
        else:
            logger.log("Adding new glyph, " + targetglyphname, "I")
            glyphstatus = "New"
            # create glyph, using targetglyphname, targetglyphunicode
            targetglyph = ufo.Uglif(layer=infont.deflayer, name=targetglyphname)
            # actually add the glyph to the font
            infont.deflayer.addGlyph(targetglyph)

        targetglyph.add('advance',{'width': str(xadvance)} )
        if targetglyphunicode: # remove any existing unicode value(s) before adding unicode value
            for i in xrange(len(targetglyph['unicode'])-1,-1,-1):
                targetglyph.remove('unicode',index=i)
            targetglyph.add('unicode',{'hex': targetglyphunicode} )
        targetglyph.add('outline')
        # to the outline element, add a component element for every entry in componentlist
        for compdic in componentlist:
            comp = ufo.Ucomponent(targetglyph['outline'],ET.Element('component',compdic))
            targetglyph['outline'].appendobject(comp,'component')
        # copy anchors to new glyph from targetglyphanchors which has format {'U': (500,1000), 'L': (500,0)}
        for a in sorted(targetglyphanchors):
            if removeRE is not None and removeRE.match(a):
                logger.log("Skipping unwanted anchor " + a, "V")
                continue  # skip this anchor
            if a not in preservedAPs:
                targetglyph.add('anchor', {'name': a, 'x': str(targetglyphanchors[a][0]), 'y': str(targetglyphanchors[a][1])} )
        # mark glyphs as being generated by setting cell mark color if -c or --colors set
        if colors:
            # Need to see if the target glyph has changed.
            if glyphstatus == "Replace":
                # Need to recreate the xml element then normalize it for comparison with original
                targetglyph.rebuildET()
                attribOrder = params['attribOrders']['glif'] if 'glif' in params['attribOrders'] else {}
                if params["sortDicts"] or params["precision"] is not None: ufo.normETdata(targetglyph.etree, params, 'glif')
                etw = ETWriter(targetglyph.etree, attributeOrder=attribOrder, indentIncr=params["indentIncr"],
                                   indentFirst=params["indentFirst"], indentML=params["indentML"], precision=params["precision"],
                                   floatAttribs=params["floatAttribs"], intAttribs=params["intAttribs"])
                newxml = etw.serialize_xml()
                if newxml == targetglyph.inxmlstr: glyphstatus = 'Unchanged'

            x = 0 if glyphstatus == "Unchanged" else 1 if glyphstatus == "Replace" else 2

            color = colors[x]
            lib = targetglyph["lib"]
            if color[0]: # Need to set actual color
                if lib is None: targetglyph.add("lib")
                targetglyph["lib"].setval("public.markColor", "string", color[0])
                logger.log(logstatuses[x] + " - setting markColor to " + color[2], "I")
            elif x < 2: # No need to log for new glyphs
                if color[1] == "none": # Remove existing color
                    if lib is not None and "public.markColor" in lib: lib.remove("public.markColor")
                    logger.log(logstatuses[x] + " - Removing existing markColor", "I")
                else:
                    logger.log(logstatuses[x] + " - Leaving existing markColor (if any)", "I")

    # If analysis only, return without writing output font
    if args.analysis: return
    # Return changed font and let execute() write it out
    return infont

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

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
