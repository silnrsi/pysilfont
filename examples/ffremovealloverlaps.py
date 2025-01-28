#!/usr/bin/env python3
from __future__ import unicode_literals
'FontForge: Remove overlap on all glyphs in font'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute


''' This  will need updating, since FontForge is no longer supported as a tool by execute() So:
- ifont and ofont will need to be changed to have type 'filename'
- ifont will then need to be opened using fontforge.open
- The font will need to be saved with font.save
- execute will need to be called with the tool set to None instead of "FF"
'''


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
