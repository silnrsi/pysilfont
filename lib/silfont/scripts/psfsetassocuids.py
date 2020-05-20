#!/usr/bin/env python
__doc__ = '''Add associate UID info to glif lib based on a csv file
- Could be one value for variant UIDs and multiple for ligatures'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from xml.etree import ElementTree as ET

suffix = "_AssocUIDs"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})]

def doit(args) :
    font = args.ifont
    incsv = args.input
    incsv.minfields = 2
    incsv.logger = font.logger
    glyphlist = list(font.deflayer.keys()) # Identify which glifs have not got AssocUIDs set

    for line in incsv :
        glyphn = line.pop(0)
        if glyphn in glyphlist :
            glyph = font.deflayer[glyphn]
            if glyph["lib"] is None : glyph.add("lib")
            # Create an array element for the UID value(s)
            array = ET.Element("array")
            for UID in line:
                sub = ET.SubElement(array,"string")
                sub.text = UID
            glyph["lib"].setelem("org.sil.assocUIDs",array)
            glyphlist.remove(glyphn)
        else :
            font.logger.log("No glyph in font for " + glyphn + " on line " + str(incsv.line_num),"E")

    for glyphn in glyphlist : # Remove any values from remaining glyphs
        glyph = font.deflayer[glyphn]
        if glyph["lib"] :
            if "org.sil.assocUIDs" in glyph["lib"] :
                glyph["lib"].remove("org.sil.assocUIDs")
                font.logger.log("UID info removed for " + glyphn,"I")

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
