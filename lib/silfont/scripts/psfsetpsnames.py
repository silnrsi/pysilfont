#!/usr/bin/env python
'''Add public.postscriptNames to lib.plist based on a csv file in one of two formats:
    - simple glyphname, postscriptname with no headers
    - with headers, where column 1 is glyph name and header for postscript name is "ps_name"'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from xml.etree import cElementTree as ET

argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont', {'help': 'Output font file', 'nargs': '?'}, {'type': 'outfont'}),
    ('-i', '--input', {'help': 'Input csv file'}, {'type': 'incsv', 'def': 'glyph_data.csv'}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': 'setpsnames.log'})]


def doit(args):
    font = args.ifont
    logger = args.logger
    incsv = args.input
    glyphlist = font.deflayer.keys()  # List to check every glyph has a psname supplied

    # Identify file format from first line
    fl = incsv.firstline
    if fl is None: logger.log("Empty imput file", "S")
    numfields = len(fl)
    incsv.numfields = numfields
    if numfields == 2:
        psnamepos = 1    # Default for plain csv
    elif numfields > 2:  # More than 2 columns, so must have standard headers
        if "ps_name" in fl:
            psnamepos = fl.index("ps_name")
            if psnamepos == 0: logger.log("First field must be glyph name, not ps_name", "S")
        else:
            logger.log("No ps_name field in csv headers", "S")
        next(incsv.reader, None)  # Skip first line with headers in
    else:
        logger.log("Invalid csv file", "S")

    # Now process the data
    dict = ET.Element("dict")
    for line in incsv:
        glyphn = line[0]
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

    for glyphn in glyphlist: logger.log("No PS name in input file for font glyph " + glyphn, "I")

    return font


def cmd(): execute("UFO", doit, argspec)
if __name__ == "__main__": cmd()
