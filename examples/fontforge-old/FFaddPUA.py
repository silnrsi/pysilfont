#!/usr/bin/env python
'''FontForge: Add cmap entries for all glyphs in the font'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'})
]

def nextpua(p) :
    if p == 0 : return 0xE000
    if p == 0xF8FF : return 0xF0000
    return p + 1

def doit(args) :
    p = nextpua(0)
    font = args.ifont
    for n in font :
        g = font[n]
        if g.unicode == -1 :
            g.unicode = p
            p = nextpua(p)
    return font

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
