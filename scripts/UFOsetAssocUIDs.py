#!/usr/bin/env python 
'''Add associate UID info to glif lib based on a csv file
  - Could be one value for variant UIDs and multiple for ligatures'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.UFOlib import *

suffix = "_AssocUIDs"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': suffix}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'infile', 'def': suffix+'.csv'}),    
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('-v','--version',{'help': 'UFO version to output'},{}),
    ('-p','--params',{'help': 'Font output parameters','action': 'append'}, {'type': 'optiondict'})]

def doit(args) :
    font = args.ifont
    csv = args.input
    glyphlist = font.deflayer.keys() # Identify which glifs have not got AssocUIDs set
    
    for l in csv.readlines() :
        l = l.strip()
        if l == "" or l[0] == "#" : continue # Skip blank lines and comments
        line = l.split(",")
        if len(line) < 2 : font.logger.log("Invalid line in csv: " + l,"E") ; continue
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
            font.logger.log("No glyph in font for " + glyphn,"E")

    for glyphn in glyphlist : # Remove any values from remaining glyphs
        glyph = font.deflayer[glyphn]
        if glyph["lib"] :
            if "org.sil.assocUIDs" in glyph["lib"] :
                glyph["lib"].remove("org.sil.assocUIDs")
                font.logger.log("UID info removed for " + glyphn,"I")
 
    return font
    
execute("PSFU",doit, argspec)