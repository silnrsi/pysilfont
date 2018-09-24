#!/usr/bin/env python
from __future__ import unicode_literals
"""Copy glyphs from one UFO to another"""
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from xml.etree import cElementTree as ET
from silfont.core import execute
from silfont.ufo import makeFileName, Uglif
import re

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-s','--source',{'help': 'Font to get glyphs from'}, {'type': 'infont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': 'glyphlist.csv'}),
    ('-f','--force',{'help' : 'Overwrite existing glyphs in the font', 'action' : 'store_true'}, {}),
    ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': '_copy.log'}),
    ('-n', '--name', {'help': 'Include glyph named name', 'action': 'append'}, {}),
    ('--rename',{'help' : 'Rename glyphs to names in this column'}, {}),
    ('--unicode', {'help': 'Re-encode glyphs to USVs in this column'}, {}),
    ('--scale',{'type' : float, 'help' : 'Scale glyphs by this factor'}, {})
]

class Glyph:
    """details about a glyph we have, or need to, copy; mostly just for syntatic sugar"""

    # Glyphs that are used *only* as component glyphs may have to be renamed if there already exists a glyph
    # by the same name in the target font. we compute a new name by appending .copy1, .copy2, etc until we get a
    # unique name. We keep track of the mapping from source font glyphname to target font glyphname using a dictionary.
    # For ease of use, glyphs named by the input file (which won't have their names changed, see --force) will also
    # be added to this dictionary because they can also be used as components.
    nameMap = dict()

    def __init__(self, oldname, newname="", psname="", dusv=None):
        self.oldname = oldname
        self.newname = newname or oldname
        self.psname = psname or None
        self.dusv = dusv or None
        # Keep track of old-to-new name mapping
        Glyph.nameMap[oldname] = self.newname


# Mapping from decimal USV to glyphname in target font
dusv2gname = None

# RE for parsing glyph names and peeling off the .copyX if present in order to search for a unique name to use:
gcopyRE = re.compile(r'(^.+?)(?:\.copy(\d+))?$')


def copyglyph(sfont, tfont, g, args):
    """copy glyph from source font to target font"""
    # Generally, 't' variables are target, 's' are source. E.g., tfont is target font.

    global dusv2gname
    if not dusv2gname:
        # Create mappings to find exsting glyph name from decimal usv:
        dusv2gname = {int(unicode.hex, 16): gname for gname in tfont.deflayer for unicode in tfont.deflayer[gname]['unicode']}
        # NB: Assumes font is well-formed and has at most one glyph with any particular Unicode value.

    # The layer where we want the copied glyph:
    tlayer = tfont.deflayer

    # if new name present in target layer, delete it.
    if g.newname in tlayer:
        # New name is already in font:
        tfont.logger.log("Replacing glyph '{0}' with new glyph".format(g.newname), "V")
        glyph = tlayer[g.newname]
        # While here, remove from our mapping any Unicodes from the old glyph:
        for unicode in glyph["unicode"]:
            dusv = int(unicode.hex, 16)
            if dusv in dusv2gname:
                del dusv2gname[dusv]
        # Ok, remove old glyph from the layer
        tlayer.delGlyph(g.newname)
    else:
        # New name is not in the font:
        tfont.logger.log("Adding glyph '{0}'".format(g.newname), "V")

    # Create new glyph
    glyph = Uglif(layer = tlayer)
    # Set etree from source glyph
    glyph.etree = ET.fromstring(sfont.deflayer[g.oldname].inxmlstr)
    glyph.process_etree()
    # Rename the glyph if needed
    if glyph.name != g.newname:
        # Use super to bypass normal glyph renaming logic since it isn't yet in the layer
        super(Uglif, glyph).__setattr__("name", g.newname)
    # add new glyph to layer:
    tlayer.addGlyph(glyph)
    tfont.logger.log("Added glyph '{0}'".format(g.newname), "V")

    # todo: set psname if requested; adjusting any other glyphs in the font as needed.

    # Adjust encoding of new glyph
    if args.unicode:
        # First remove any encodings the copied glyph had in the source font:
        for i in range(len(glyph['unicode']) - 1, -1, -1):
            glyph.remove('unicode', index=i)
        if g.dusv:
            # we want this glyph to be encoded.
            # First remove this Unicode from any other glyph in the target font
            if g.dusv in dusv2gname:
                oglyph = tlayer[dusv2gname[g.dusv]]
                for unicode in oglyph["unicode"]:
                    if int(unicode.hex,16) == g.dusv:
                        oglyph.remove("unicode", object=unicode)
                        tfont.logger.log("Removed USV {0:04X} from existing glyph '{1}'".format(g.dusv,dusv2gname[g.dusv]), "V")
                        break
            # Now add and record it:
            glyph.add("unicode", {"hex": '{:04X}'.format(g.dusv)})
            dusv2gname[g.dusv] = g.newname
            tfont.logger.log("Added USV {0:04X} to glyph '{1}'".format(g.dusv, g.newname), "V")

    # Scale glyph if desired
    if args.scale:
        for e in glyph.etree.getiterator():
            for attr in ('width', 'height', 'x', 'y', 'xOffset', 'yOffset'):
                if attr in e.attrib: e.set(attr, str(int(float(e.get(attr))* args.scale)))

    # Look through components, adjusting names and finding out if we need to copy some.
    for component in glyph.etree.findall('./outline/component[@base]'):
        oldname = component.get('base')
        # Note: the following will cause recursion:
        component.set('base', copyComponent(sfont, tfont, oldname ,args))



def copyComponent(sfont, tfont, oldname, args):
    """copy component glyph if not already copied; make sure name and psname are unique; return its new name"""
    if oldname in Glyph.nameMap:
        # already copied
        return Glyph.nameMap[oldname]

    # if oldname is already in the target font, make up a new name by adding ".copy1", incrementing as necessary
    if oldname not in tfont.deflayer:
        newname = oldname
        tfont.logger.log("Copying component '{0}' with existing name".format(oldname), "V")
    else:
        x = gcopyRE.match(oldname)
        base = x.group(1)
        try: i = int(x.group(2))
        except: i = 1
        while "{0}.copy{1}".format(base,i) in tfont.deflayer:
            i += 1
        newname = "{0}.copy{1}".format(base,i)
        tfont.logger.log("Copying component '{0}' with new name '{1}'".format(oldname, newname), "V")

    # todo: something similar to above but for psname

    # Now copy the glyph, giving it new name if needed.
    copyglyph(sfont, tfont, Glyph(oldname, newname), args)

    return newname

def doit(args) :
    sfont = args.source  # source UFO
    tfont = args.ifont   # target UFO
    incsv = args.input
    logger = args.logger

    # Get headings from csvfile:
    fl = incsv.firstline
    if fl is None: logger.log("Empty imput file", "S")
    numfields = len(fl)
    # defaults for single column csv (no headers):
    nameCol = 0
    renameCol = None
    psCol = None
    usvCol = None
    if numfields > 1 or args.rename or args.unicode:
        # required columns:
        try:
            nameCol = fl.index('glyph_name');
            if args.rename:
                renameCol = fl.index(args.rename);
            if args.unicode:
                usvCol = fl.index(args.unicode);
        except ValueError as e:
            logger.log('Missing csv input field: ' + e.message, 'S')
        except Exception as e:
            logger.log('Error reading csv input field: ' + e.message, 'S')
        # optional columns
        psCol  = fl.index('ps_name') if 'ps_name' in fl else None
    if 'glyph_name' in fl:
        next(incsv.reader, None)  # Skip first line with headers in

    # list of glyphs to copy
    glist = list()

    def checkname(oldname, newname = None):
        if not newname: newname = oldname
        if oldname in Glyph.nameMap:
            logger.log("Line {0}: Glyph '{1}' specified more than once; only the first kept".format(incsv.line_num, oldname), 'W')
        elif oldname not in sfont.deflayer:
            logger.log("Line {0}: Glyph '{1}' is not in source font; skipping".format(incsv.line_num, oldname),"W")
        elif newname in tfont.deflayer and not args.force:
            logger.log("Line {0}: Glyph '{1}' already present; skipping".format(incsv.line_num, newname), "W")
        else:
            return True
        return False

    # glyphs specified in csv file
    for r in incsv:
        oldname = r[nameCol]
        newname = r[renameCol] if args.rename else oldname
        psname = r[psCol] if psCol is not None else None
        if args.unicode and r[usvCol]:
            # validate USV:
            try:
                dusv = int(r[usvCol],16)
            except ValueError:
                logger.log("Line {0}: Invalid USV '{1}'; ignored.".format(incsv.line_num, r[usvCol]), "W")
                dusv = None
        else:
            dusv = None

        if checkname(oldname, newname):
            glist.append(Glyph(oldname, newname, psname, dusv))

    # glyphs specified on the command line
    if args.name:
        for gname in args.name:
            if checkname(gname):
                glist.append(Glyph(gname))

    # Ok, now process them:
    if len(glist) == 0:
        logger.log("No glyphs to copy", "S")

    # copy glyphs by name
    while len(glist) :
        g = glist.pop(0)
        tfont.logger.log("Copying source glyph '{0}' as '{1}'{2}".format(g.oldname, g.newname,
                         " (U+{0:04X})".format(g.dusv) if g.dusv else ""), "I")
        copyglyph(sfont, tfont, g, args)

    return tfont

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
