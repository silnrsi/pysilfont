#!/usr/bin/env python
__doc__ = '''Load glyph order data into public.glyphOrder in lib.plist based on based on a text file in one of two formats:
    - simple text file with one glyph name per line
    - csv file with headers, using headers "glyph_name" and "sort_final" where the latter contains
      numeric values used to sort the glyph names by'''
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
    ('--header', {'help': 'Column header(s) for sort order', 'default': 'sort_final'}, {}),
    ('--field', {'help': 'Field(s) in lib.plist to update', 'default': 'public.glyphOrder'}, {}),
    ('-i', '--input', {'help': 'Input text file, one glyphname per line'}, {'type': 'incsv', 'def': 'glyph_data.csv'}),
    ('-x', '--removemissing', {'help': 'Remove from list if glyph not in font', 'action': 'store_true', 'default': False}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_gorder.log'})]


def doit(args):
    font = args.ifont
    incsv = args.input
    logger = args.logger
    removemissing = args.removemissing

    fields = args.field.split(",")
    fieldcount = len(fields)
    headers = args.header.split(",")
    if fieldcount != len(headers): logger.log("Must specify same number of values in --field and --header", "S")
    gname = args.gname

    # Identify file format from first line then create glyphdata[] with glyph name then one column per header
    glyphdata = {}
    fl = incsv.firstline
    if fl is None: logger.log("Empty input file", "S")
    numfields = len(fl)
    incsv.numfields = numfields
    fieldpos = []
    if numfields > 1:  # More than 1 column, so must have headers
        if gname in fl:
            glyphnpos = fl.index(gname)
        else:
            logger.log("No" + gname + "field in csv headers", "S")
        for header in headers:
            if header in fl:
                pos = fl.index(header)
                fieldpos.append(pos)
            else:
                logger.log('No "' + header + '" heading in csv headers"', "S")
        next(incsv.reader, None)  # Skip first line with headers in
        for line in incsv:
            glyphn = line[glyphnpos]
            if len(glyphn) == 0:
                continue	# No need to include cases where name is blank
            glyphdata[glyphn]=[]
            for pos in fieldpos: glyphdata[glyphn].append(float(line[pos]))
    elif numfields == 1:   # Simple text file.  Create glyphdata in same format as for csv files
        for i, line in enumerate(incsv): glyphdata[line[0]]=(i,)
    else:
        logger.log("Invalid csv file", "S")

    # Now process the data
    if "lib" not in font.__dict__: font.addfile("lib")
    glyphlist = list(font.deflayer.keys())

    for i in range(0,fieldcount):
        array = ET.Element("array")
        for glyphn, vals in sorted(glyphdata.items(), key=lambda item: item[1][i]):
            if glyphn in glyphlist:
                sub = ET.SubElement(array, "string")
                sub.text = glyphn
            else:
                font.logger.log("No glyph in font for " + glyphn, "I")
                if not removemissing:
                    sub = ET.SubElement(array, "string")
                    sub.text = glyphn
        font.lib.setelem(fields[i-1],array)

    for glyphn in sorted(glyphlist):  # Remaining glyphs were not in the input file
        if glyphn not in glyphdata: font.logger.log("No entry in input file for font glyph " + glyphn, "I")

    return font


def cmd(): execute("UFO", doit, argspec) 
if __name__ == "__main__": cmd()
