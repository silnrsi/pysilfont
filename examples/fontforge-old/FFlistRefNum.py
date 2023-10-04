#!/usr/bin/env python3
'FontForge: Report Glyph name, Number of references (components)'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

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

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
