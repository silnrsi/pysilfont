#!/usr/bin/env python3
'FontForge: List all the data in a glyph object in key, value pairs'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import fontforge, types, sys
from silfont.core import execute

argspec = [
    ('font',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output text file'}, {'type': 'outfile', 'def': 'glyphinfo.txt'})]


def doit(args) :
    font=args.font
    outf = args.output

    glyphn = raw_input("Glyph name or number: ")

    while glyphn:

        isglyph=True
        if not(glyphn in font):
            try:
                glyphn=int(glyphn)
            except ValueError:
                isglyph=False
            else:
                if not(glyphn in font):
                    isglyph=False

        if isglyph:
            g=font[glyphn]
            outf.write("\n%s\n\n" % glyphn)
            # Write to file all normal key,value pairs - exclude __ and built in functions
            for k in dir(g):
                if k[0:2] == "__": continue
                attrk=getattr(g,k)
                if attrk is None: continue
                tk=type(attrk)
                if tk == types.BuiltinFunctionType: continue
                if k == "ttinstrs": # ttinstr values are not printable characters
                    outf.write("%s,%s\n" % (k,"<has values>"))
                else:
                    outf.write("%s,%s\n" % (k,attrk))
            # Write out all normal keys where value is none
            for k in dir(g):
                attrk=getattr(g,k)
                if attrk is None:
                    outf.write("%s,%s\n" % (k,attrk))
        else:
            print "Invalid glyph"

        glyphn = raw_input("Glyph name or number: ")
    print "done"
    outf.close

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
