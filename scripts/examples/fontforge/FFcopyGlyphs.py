#!/usr/bin/env python
'''FontForge: Copy glyphs from one font to another, without using ffbuilder'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.genlib import execute
import psMat

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('-i','--input',{'help': 'Font to get glyphs from', 'required' : True}, {'type': 'infont'}),
    ('-r','--range',{'help': 'StartUnicode..EndUnicode no spaces, e.g. 20..7E', 'action' : 'append'}, {}),
    ('--rangefile',{'help': 'File with USVs e.g. 20 or a range e.g. 20..7E or both', 'action' : 'append'}, {}),
    ('-n','--name',{'help': 'Include glyph named name', 'action' : 'append'}, {}),
    ('-a','--anchors',{'help' : 'Copy across anchor points', 'action' : 'store_true'}, {}),
    ('-f','--force',{'help' : 'Overwrite existing glyphs in the font', 'action' : 'store_true'}, {}),
    ('-s','--scale',{'type' : float, 'help' : 'Scale glyphs by this factor'}, {})
]

def copyglyph(font, infont, g, u, args) :
    if args.scale is None :
        scale = psMat.identity()
    else :
        scale = psMat.scale(args.scale)
    o = font.findEncodingSlot(u)
    if o == -1 :
        glyph = font.createChar(u, g.glyphname)
    else :
        glyph = font[o]
    font.selection.select(glyph)
    pen = glyph.glyphPen()
    g.draw(pen)
    glyph.transform(scale)
    glyph.width = g.width * scale[0]
    if args.anchors :
        for a in g.anchorPoints :
            try :
                l = font.getSubtableOfAnchor(a[1])
            except EnvironmentError :
                font.addAnchorClass("", a[0]*scale[0], a[1]*scale[0])
        glyph.anchorPoints = g.anchorPoints

def doit(args) :
    font = args.ifont
    infont = args.input
    font.encoding = "Original"
    infont.encoding = "Original"    # compact the font so findEncodingSlot will work
    infont.layers["Fore"].is_quadratic = font.layers["Fore"].is_quadratic
    ulist = list()

    # characters specified on the command line
    for r in args.range or [] :
        (rstart, rend) = map(lambda x: int(x,16), r.split('..'))
        for u in range(rstart, rend + 1) :
            ulist.append(u)

    # characters specified in a file
    for filename in args.rangefile or [] :
        rangefile = file(filename, 'r')
        for line in rangefile :
            # ignore comments
            line = line.partition('#')[0]
            line = line.strip()

            # ignore blank lines
            if (line == ''):
                continue

            # obtain USVs
            try:
                (rstart, rend) = line.split('..')
            except ValueError:
                rstart = line
                rend = line

            rstart = int(rstart, 16)
            rend = int(rend, 16)

            for u in range(rstart, rend + 1):
                ulist.append(u)

    # copy the characters from the generated list
    for u in ulist:
        o = font.findEncodingSlot(u)
        if o != -1 and not args.force :
            print "Glyph for %x already present. Skipping" % u
            continue
        e = infont.findEncodingSlot(u)
        if e == -1 :
            print "Can't find glyph for %04X" % u
            continue
        g = infont[e]
        copyglyph(font, infont, g, u, args)

    # copy glyphs by name
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
