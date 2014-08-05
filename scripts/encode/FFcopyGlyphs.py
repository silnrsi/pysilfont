#!/usr/bin/env python
'''FontForge: Copy glyphs from one font to another, without using ffbuilder'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'
__version__ = '0.0.1'

from silfont.fontforge.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('-i','--input',{'help': 'Font to get glyphs from', 'required' : True}, {'type': 'infont'}),
    ('-r','--range',{'help': 'StartUnicode..EndUnicode no spaces, e.g. 20..7E', 'action' : 'append'}, {})]

def doit(args) :
    font = args.ifont
    infont = args.input
    infont.layers["Fore"].is_quadratic = font.layers["Fore"].is_quadratic
    for r in args.range :
        (rstart, rend) = map(lambda x: int(x,16), r.split('..'))
        for u in range(rstart, rend + 1) :
            o = font.findEncodingSlot(u)
            if o != -1 :
                print "Glyph for %x already present. Skipping" % u
                continue
            e = infont.findEncodingSlot(u)
            if e == -1 :
                print "Can't find glyph for %x" % u
                continue
            g = infont[e]
            glyph = font.createChar(u, g.glyphname)
            font.selection.select(glyph)
            pen = glyph.glyphPen()
            g.draw(pen)
            glyph.width = g.width
    return font

execute(doit, argspec)
