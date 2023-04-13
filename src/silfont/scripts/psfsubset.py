#!/usr/bin/env python3
__doc__ = '''Subset an existing UFO based on a csv or text list of glyph names or USVs to keep.
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.core import execute
from xml.etree import ElementTree as ET
import re

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv'}),
    ('--header', {'help': 'Column header for glyphlist', 'default': 'glyph_name'}, {}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_subset.log'})]

def doit(args) :
    font = args.ifont
    incsv = args.input
    logger = args.logger
    deflayer = font.deflayer

    # Create mappings to find glyph name from decimal usv:
    dusv2gname = {int(ucode.hex, 16): gname for gname in deflayer for ucode in deflayer[gname]['unicode']}

    # check for headers in the csv
    fl = incsv.firstline
    if fl is None: logger.log("Empty input file", "S")
    numfields = len(fl)
    if numfields == 1 and args.header not in fl:
        dataCol = 0       # Default for plain csv
    elif numfields >= 1:  # Must have headers
        try:
            dataCol = fl.index(args.header)
        except ValueError as e:
            logger.log('Missing csv input field: ' + e.message, 'S')
        except Exception as e:
            logger.log('Error reading csv input field: ' + e.message, 'S')
        next(incsv.reader, None)  # Skip first line with headers in
    else:
        logger.log("Invalid csv file", "S")

    # From the csv, assemble a list of glyphs to process:
    toProcess = set()
    usvRE = re.compile('[0-9a-f]{4,6}',re.IGNORECASE)   # matches 4-6 digit hex
    for r in incsv:
        gname = r[dataCol].strip()
        if usvRE.match(gname):
            # data is USV, not glyph name
            dusv = int(gname,16)
            if dusv in dusv2gname:
                toProcess.add(dusv2gname[dusv])
                continue
            # The USV wasn't in the font... try it as a glyph name
        if gname not in deflayer:
            logger.log("Glyph '%s' not in font; line %d ignored" % (gname, incsv.line_num), 'W')
            continue
        toProcess.add(gname)

    # Generate a complete list of glyphs to keep:
    toKeep = set()
    while len(toProcess):
        gname = toProcess.pop()   # retrieves a random item from the set
        if gname in toKeep:
            continue    # Already processed this one
        toKeep.add(gname)
        
        # If it has any components we haven't already processed, add them to the toProcess list
        for component in deflayer[gname].etree.findall('./outline/component[@base]'):
            cname = component.get('base')
            if cname not in toKeep:
                toProcess.add(cname)

    # Generate a complete list of glyphs to delete:
    toDelete = set(deflayer).difference(toKeep)

    # Remove any glyphs not in the toKeep set
    for gname in toDelete:
        logger.log("Deleting " + gname, "V")
        deflayer.delGlyph(gname)
    assert len(deflayer) == len(toKeep), "len(deflayer) != len(toKeep)"
    logger.log("Retained %d glyphs, deleted %d glyphs." % (len(toKeep), len(toDelete)), "P")

    # Clean up and rebuild sort orders
    libexists = True if "lib" in font.__dict__ else False
    for orderName in ('public.glyphOrder', 'com.schriftgestaltung.glyphOrder'):
        if libexists and orderName in font.lib:
            glyphOrder = font.lib.getval(orderName)  # This is an array
            array = ET.Element("array")
            for gname in glyphOrder:
                if gname in toKeep:
                    ET.SubElement(array, "string").text = gname
            font.lib.setelem(orderName, array)

    # Clean up and rebuild psnames
    if libexists and 'public.postscriptNames' in font.lib:
        psnames = font.lib.getval('public.postscriptNames')  # This is a dict keyed by glyphnames
        dict = ET.Element("dict")
        for gname in psnames:
            if gname in toKeep:
                ET.SubElement(dict, "key").text = gname
                ET.SubElement(dict, "string").text = psnames[gname]
        font.lib.setelem("public.postscriptNames", dict)

    return font

def cmd() : execute("UFO",doit,argspec) 

if __name__ == "__main__": cmd()
