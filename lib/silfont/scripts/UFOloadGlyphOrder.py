#!/usr/bin/env python
'''Load glyph order data into lib.plist based on a text file'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from xml.etree import cElementTree as ET

suffix = "_Gorder"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('--GlyphsApp',{'help': 'Load display order for Glyphs app rather than public.glyphOrder', 'action': 'store_true'},{}),
    ('-i','--input',{'help': 'Input text file, one glyphname per line'}, {'type': 'infile', 'def': suffix+'.txt'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})]

def doit(args) :
    font = args.ifont
    infile = args.input
    glyphlist = font.deflayer.keys() # List to check every glyph has a record in the list

    array = ET.Element("array")

    for glyphn in infile.readlines() :
        glyphn = glyphn.strip()
        if glyphn == "" or glyphn[0] == "#" : continue
        # Add to array
        sub = ET.SubElement(array,"string")
        sub.text = glyphn
        # Check to see if glyph is in font
        if glyphn in glyphlist :
            glyphlist.remove(glyphn) # So glyphlist ends up with those without an entry
        else :
            font.logger.log("No glyph in font for " + glyphn,"I")

    for glyphn in glyphlist : # Remaining glyphs were not in the input file
        font.logger.log("No entry in input file for font glyph " + glyphn,"I")

    # Add to lib.plist
    if "lib" not in font.__dict__ : #@@@ Need to extend capability of Uplist to do much of this
        font.lib = Uplist(font = font)
        font.dtree['lib.plist'] = dirTreeItem(read = True, added = True, fileObject = font.lib, fileType = "xml")
        font.lib.etree = ET.fromstring("<plist>\n<dict/>\n</plist>")
    if args.GlyphsApp:
        font.lib.setelem("com.schriftgestaltung.glyphOrder",array)
    else:
        font.lib.setelem("public.glyphOrder",array)

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
