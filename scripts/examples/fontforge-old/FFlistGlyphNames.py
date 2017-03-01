#!/usr/bin/env python
'FontForge: List all gyphs with encoding and name'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output text file'}, {'type': 'outfile', 'def': 'Gnames.txt'})]

def doit(args) :
    outf = args.output
    for glyph in args.ifont:
        g = args.ifont[glyph]
        outf.write('%s: %s, %s\n' % (glyph, g.encoding, g.glyphname))
    outf.close()

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
