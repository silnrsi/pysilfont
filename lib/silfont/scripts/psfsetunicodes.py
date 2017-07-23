#!/usr/bin/env python
'''Set the unicodes of glyphs in a font based on an external file. Note that this will not currently remove any unicode values that already exist in unlisted glyphs
- csv format glyphname,unicode'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney, based on UFOsetPSnames.py'

from silfont.core import execute

suffix = "_updated"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})]

def doit(args) :
    font = args.ifont
    incsv = args.input
    incsv.numfields = 2
    incsv.logger = font.logger
    
    glyphlist = font.deflayer.keys()

    for line in incsv :
        glyphn = line[0]
        unival = line[1]

        if glyphn in glyphlist :
            glyph = font.deflayer[glyphn]
            if len(glyph["unicode"]) == 1 :
                glyph.remove("unicode",index = 0)
            glyph.add("unicode",{"hex": unival})
            glyphlist.remove(glyphn)
        else :
            font.logger.log("No glyph in font for " + glyphn  + " on line " + str(incsv.line_num), "I")

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
