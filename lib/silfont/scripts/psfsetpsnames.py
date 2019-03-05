#!/usr/bin/env python
from __future__ import unicode_literals
'''Add public.postscriptNames to lib.plist based on a csv file in one of two formats:
    - simple glyphname, postscriptname with no headers
    - with headers, where the headers for glyph name and postscript name "glyph_name" and "ps_name"'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from xml.etree import ElementTree as ET

argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont', {'help': 'Output font file', 'nargs': '?'}, {'type': 'outfont'}),
    ('--gname', {'help': 'Column header for glyph name', 'default': 'glyph_name'}, {}),
    ('-i', '--input', {'help': 'Input csv file'}, {'type': 'incsv', 'def': 'glyph_data.csv'}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': 'setpsnames.log'})]


def doit(args):
    font = args.ifont
    logger = args.logger
    incsv = args.input
    gname = args.gname
    glyphlist = list(font.deflayer.keys())  # List to check every glyph has a psname supplied

    # Identify file format from first line
    fl = incsv.firstline
    if fl is None: logger.log("Empty imput file", "S")
    numfields = len(fl)
    incsv.numfields = numfields
    if numfields == 2:
        glyphnpos = 0
        psnamepos = 1    # Default for plain csv
    elif numfields > 2:  # More than 2 columns, so must have standard headers
        if gname in fl:
            glyphnpos = fl.index(gname)
        else:
            logger.log("No " + gname + " field in csv headers", "S")
        if "ps_name" in fl:
            psnamepos = fl.index("ps_name")
        else:
            logger.log("No ps_name field in csv headers", "S")
        next(incsv.reader, None)  # Skip first line with headers in
    else:
        logger.log("Invalid csv file", "S")

    # Now process the data
    dict = ET.Element("dict")
    for line in incsv:
        glyphn = line[glyphnpos]
        psname = line[psnamepos]
        if len(psname) == 0 or glyphn == psname:
            continue	# No need to include cases where production name is blank or same as working name
        # Add to dict
        sub = ET.SubElement(dict, "key")
        sub.text = glyphn
        sub = ET.SubElement(dict, "string")
        sub.text = psname
        # Check if in font
        if glyphn in glyphlist:
            glyphlist.remove(glyphn)
        else:
            logger.log("No glyph in font for " + glyphn + " on line " + str(incsv.line_num), "I")
    # Add to lib.plist
    if len(dict) > 0:
        if "lib" not in font.__dict__: font.addfile("lib")
        font.lib.setelem("public.postscriptNames", dict)
    else:
        if "lib" in font.__dict__ and "public.postscriptNames" in font.lib:
            font.lib.remove("public.postscriptNames")

    for glyphn in sorted(glyphlist): logger.log("No PS name in input file for font glyph " + glyphn, "I")

    return font


def cmd(): execute("UFO", doit, argspec)
if __name__ == "__main__": cmd()
