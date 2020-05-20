#!/usr/bin/env python
__doc__ = '''Add associate feature info to glif lib based on a csv file
csv format glyphname,featurename[,featurevalue]'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

suffix = "_AssocFeat"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})]

def doit(args) :
    font = args.ifont
    incsv = args.input
    incsv.minfields = 2
    incsv.maxfields = 3
    incsv.logger = font.logger
    glyphlist = list(font.deflayer.keys()) # Identify which glifs have not got an AssocFeat set

    for line in incsv :
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
            font.logger.log("No glyph in font for " + glyphn + " on line " + str(incsv.line_num),"E")

    for glyphn in glyphlist : # Remove any values from remaining glyphs
        glyph = font.deflayer[glyphn]
        if glyph["lib"] :
            if "org.sil.assocFeatureValue" in glyph["lib"] : glyph["lib"].remove("org.sil.assocFeatureValue")
            if "org.sil.assocFeature" in glyph["lib"] :
                glyph["lib"].remove("org.sil.assocFeature")
                font.logger.log("Feature info removed for " + glyphn,"I")

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
