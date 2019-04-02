#!/usr/bin/env python3
'''Uses the GlyphConstruction library to build composite glyphs.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute
from glyphConstruction import ParseGlyphConstructionListFromString, GlyphConstructionBuilder

argspec = [
    ('ifont', {'help': 'Input font filename'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--cdfile',{'help': 'Composite Definitions input file'}, {'type': 'infile', 'def': 'constructions.txt'}),
    ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': '_gc.log'})]

def doit(args) :
    font = args.ifont
    logger = args.logger

    constructions = ParseGlyphConstructionListFromString(args.cdfile)

    for construction in constructions :
        # Create a new constructed glyph object
        constructionGlyph = GlyphConstructionBuilder(construction, font)
        # Make a new glyph in target font with the new glyph name
        glyph = font.newGlyph(constructionGlyph.name)
        # Draw the constructed object onto the new glyph
        # This is rather odd in how it works
        constructionGlyph.draw(glyph.getPen())
        # Copy glyph metadata from constructed object
        glyph.name = constructionGlyph.name
        glyph.unicode = constructionGlyph.unicode
        glyph.note = constructionGlyph.note
        #glyph.markColor = constructionGlyph.mark
        glyph.width = constructionGlyph.width

    return font

def cmd() : execute("FP",doit,argspec)
if __name__ == "__main__": cmd()
