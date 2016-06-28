#!/usr/bin/env python
'FontForge: Report Glyph name, Number of references (components)'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.genlib import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output text file'}, {'type': 'outfile', 'def': 'RefNum.txt'})]

def doit(args) :
    font = args.ifont
    outf = args.output

    outf.write("# glyphs with number of components\n\n")
    for glyph in font:
        gname=font[glyph].glyphname
        ref = font[glyph].references
        if ref is None:
            n=0
        else:
            n=len(ref)
        outf.write("%s %i\n" % (gname,n))
      
    outf.close()

    print "Done!"

execute("FF",doit, argspec)
