#!/usr/bin/env python 
'''Sort components and anchors to allow diff tools to detect other changes to glyphs '''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': '_normD'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'normCompAnc.log'})]

def doit(args) :
    font=args.ifont
    logf = args.log
        
    # Sort anchors and components in Glyphs alphabetically to allow diffs to be done
    for g in font:
        new=sorted(g.anchors, key=lambda anc: anc.name )
        if new <> g.anchors:
            g.anchors=new
            logf.write ("Glyph anchors reordered for " + g._name + "\n")
        new=sorted(g.components, key=lambda comp: comp.baseGlyph + str(comp.offset) )
        if new <> g.components:
            g.components=new
            logf.write ("Glyph components reordered for " + g._name + "\n")
    
    
    logf.close()
    return font

execute("RFB",doit, argspec)
