#!/usr/bin/env python
from __future__ import unicode_literals
'Generate a ttf file without OpenType tables from a UFO'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Alan Ward'

# Compared to fontmake it does not decompose glyphs or remove overlaps 
# and curve conversion seems to happen in a different way.

from silfont.core import execute
import defcon, ufo2ft.outlineCompiler, ufo2ft.preProcessor

argspec = [
    ('iufo', {'help': 'Input UFO folder'}, {}),
    ('ottf', {'help': 'Output ttf file name'}, {}),
    ('--removeOverlap', {'help': 'Merge overlapping contours', 'action': 'store_true'}, {})]

PUBLIC_PREFIX = 'public.'

def getuvss(ufo):
    uvsdict = {}
    uvs = ufo.lib.get('org.sil.uvs', None)
    if uvs is not None:
        for usv, dat in uvs.items():
            usvc = int(usv, 16)
            pairs = []
            uvsdict[usvc] = pairs
            for k, v in dat.items():
                pairs.append((int(k, 16), v))
        return uvsdict
    for g in ufo:
        uvs = getattr(g, 'lib', {}).get("org.sil.uvs", None)
        if uvs is None:
            continue
        codes = [int(x, 16) for x in uvs.split()]
        if codes[1] not in uvsdict:
            uvsdict[codes[1]] = []
        uvsdict[codes[1]].append((codes[0], (g.name if codes[0] not in g.unicodes else None)))
    return uvsdict
        

def doit(args):
    ufo = defcon.Font(args.iufo)

#    args.logger.log('Converting UFO to ttf and compiling fea')
#    font = ufo2ft.compileTTF(ufo,
#        glyphOrder = ufo.lib.get(PUBLIC_PREFIX + 'glyphOrder'),
#        useProductionNames = False)

    args.logger.log('Converting UFO to ttf without OT', 'P')

    # default arg value for TTFPreProcessor class: removeOverlaps = False, convertCubics = True
    preProcessor = ufo2ft.preProcessor.TTFPreProcessor(ufo, removeOverlaps = args.removeOverlap, convertCubics=True)
    glyphSet = preProcessor.process()
    outlineCompiler = ufo2ft.outlineCompiler.OutlineTTFCompiler(ufo,
        glyphSet=glyphSet,
        glyphOrder=ufo.lib.get(PUBLIC_PREFIX + 'glyphOrder'))
    font = outlineCompiler.compile()

    # handle uvs glyphs until ufo2ft does it for us.
    uvsdict = getuvss(ufo)
    if len(uvsdict):
        from fontTools.ttLib.tables._c_m_a_p import cmap_format_14
        cmap_uvs = cmap_format_14(14)
        cmap_uvs.platformID = 0
        cmap_uvs.platEncID = 5
        cmap_uvs.cmap = {}
        cmap_uvs.uvsDict = uvsdict
        font['cmap'].tables.append(cmap_uvs)

    args.logger.log('Saving ttf file', 'P')
    font.save(args.ottf)

    args.logger.log('Done', 'P')

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
