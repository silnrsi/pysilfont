#!/usr/bin/env python 
'''Load glyph order data into lib.plist based on a text file'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.UFOlib import *

suffix = "_Gorder"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': suffix}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'infile', 'def': suffix+'.txt'}),    
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('-v','--version',{'help': 'UFO version to output'},{}),
    ('-p','--params',{'help': 'Font output parameters','action': 'append'}, {'type': 'optiondict'})]

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
    font.lib.setelem("public.glyphOrder",array)

    return font
    
execute("PSFU",doit, argspec)
