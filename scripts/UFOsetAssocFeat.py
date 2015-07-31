#!/usr/bin/env python 
'''Add associate feature info to glif lib'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.UFOlib import *

suffix = "_AssocFeat"
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
    glyphlist = font.deflayer.keys() # Identify which glifs have not got an AssocFeat set
    
    for line in csv.readlines() :
        if line[0] == "#" : continue # Skip comments
        line = line.strip()
        if line == "" : continue # Skip blank lines
        line = line.split(",")
        if len(line) < 2 or len(line) > 3 : font.logger.log("Invalid line in csv: " + line,"E")
        glyphn = line[0]
        feature = line[1]
        value = line[2] if len(line) == 3 else ""
        
        if glyphn in glyphlist :
            glyph = font.deflayer[glyphn]
            if glyph["lib"] is None : glyph.add("lib")
            glyph["lib"].setval("org.sil.assocFeature","string",feature)
            if value is not "" :
                glyph["lib"].setval("org.sil.assocFeatureValue","integer",value)
            else :
                if "org.sil.assocFeatureValue" in glyph["lib"] : glyph["lib"].remove("org.sil.assocFeatureValue")
            glyphlist.remove(glyphn)
        else :
            font.logger.log("No glyph in font input file line for " + glyphn,"E")

    for glyphn in glyphlist : # Remove any values from remaining glyphs
        glyph = font.deflayer[glyphn]
        if glyph["lib"] :
            if "org.sil.assocFeatureValue" in glyph["lib"] : glyph["lib"].remove("org.sil.assocFeatureValue")
            if "org.sil.assocFeature" in glyph["lib"] :
                glyph["lib"].remove("org.sil.assocFeature")
                font.logger.log("Feature info removed for " + glyphn,"I")
 
    return font
    
execute("PSFU",doit, argspec)