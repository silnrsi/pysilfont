#!/usr/bin/env python 
'''Add public.poscriptname to glif lib based on a csv file
  - csv format glyphname,postscriptname'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.UFOlib import *

suffix = "_PSnames"
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
    glyphlist = font.deflayer.keys() # List to check every glyph has a psname applied
    
    for l in csv.readlines() :
        l = l.strip()
        if l == "" or l[0] == "#" : continue # Skip blank lines and comments
        line = l.split(",")
        if len(line) <> 2 : font.logger.log("Invalid line in csv: " + l,"E"); continue
        glyphn = line[0]
        psname = line[1]
 
        if glyphn in glyphlist :
            glyph = font.deflayer[glyphn]
            if glyph["lib"] is None : glyph.add("lib")
            glyph["lib"].setval("public.postscriptname","string",psname)
            glyphlist.remove(glyphn)
        else :
            font.logger.log("No glyph in font for " + glyphn,"I")

    for glyphn in glyphlist : # Remaining glyphs for which no psname was supplied
        glyph = font.deflayer[glyphn]
        if glyph["lib"] :
            if "public.postscriptname" in glyph["lib"] : glyph["lib"].remove("public.postscriptname")
        font.logger.log("No PS name in input file for font glyph " + glyphn,"I")

    return font
    
execute("PSFU",doit, argspec)