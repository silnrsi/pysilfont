#!/usr/bin/env python
'''FontForge: Copy glyphs from one font to another, without using ffbuilder'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.genlib import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('-i','--input',{'help': 'Font to get glyphs from', 'required' : True}, {'type': 'infont'}),
    ('-r','--range',{'help': 'StartUnicode..EndUnicode no spaces, e.g. 20..7E', 'action' : 'append'}, {}),
    ('-n','--name',{'help': 'Include glyph named name', 'action' : 'append'}, {}),
    ('-a','--anchors',{'help' : 'Copy across anchor points', 'action' : 'store_true'}, {})
]

def copyglyph(font, infont, g, u, args) :
    glyph = font.createChar(u, g.glyphname)
    font.selection.select(glyph)
    pen = glyph.glyphPen()
    g.draw(pen)
    glyph.width = g.width
    if args.anchors :
        for a in g.anchorPoints :
            try :
                l = font.getSubtableOfAnchor(a[1])
            except EnvironmentError :
                font.addAnchorClass("", a[0], a[1])
        glyph.anchorPoints = g.anchorPoints

def doit(args) :
    font = args.ifont
    infont = args.input
    font.encoding = "Original"
    infont.encoding = "Original"    # compact the font so findEncodingSlot will work
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
                print "Can't find glyph for %04X" % u
                continue
            g = infont[e]
            copyglyph(font, infont, g, u, args)
    for n in args.name or [] :
        if n in font :
            print "Glyph %s already present. Skipping" % n
            continue
        if n not in infont :
            print "Can't find glyph %s" % n
            continue
        g = infont[n]
        copyglyph(font, infont, g, -1, args)
    return font

execute("FF",doit, argspec)
