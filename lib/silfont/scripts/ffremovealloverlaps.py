#!/usr/bin/env python
from __future__ import unicode_literals
'FontForge: Remove overlap on all glyphs in font'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'})]

def doit(args) :
    font = args.ifont
    for glyph in font:
        font[glyph].removeOverlap()
    return font

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
