#!/usr/bin/env python
from __future__ import unicode_literals
'''Deletes glyphs from a UFO based on list. Can instead delete glyphs not in list.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute

argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont', {'help': 'Output font file', 'nargs': '?'}, {'type': 'outfont'}),
    ('-i', '--input', {'help': 'Input text file, one glyphname per line'}, {'type': 'infile', 'def': 'glyphlist.txt'}),
    ('--reverse',{'help': 'Remove glyphs not in list instead', 'action': 'store_true', 'default': False},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'deletedglyphs.log'})]

def doit(args) :
    font = args.ifont
    listinput = args.input
    logger = args.logger

    glyphlist = []
    for line in listinput.readlines():
        glyphlist.append(line.strip())

    deletelist = []

    if args.reverse:
        for glyphname in font.deflayer:
            if glyphname not in glyphlist:
                deletelist.append(glyphname)
    else:
        for glyphname in font.deflayer:
            if glyphname in glyphlist:
                deletelist.append(glyphname)

    logger.log("Deleted glyphs:")

    for deleted in sorted(deletelist):
        font.deflayer.delGlyph(deleted)
        logger.log(deleted)

    logger.log("Total deleted glyphs: " + str(len(deletelist)))

    return font

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()

