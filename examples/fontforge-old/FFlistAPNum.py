#!/usr/bin/env python3
'FontForge: Report Glyph name, number of anchors - sorted by number of anchors'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output text file'}, {'type': 'outfile', 'def': 'APnum.txt'})]

def doit(args) :
    font = args.ifont
    outf = args.output

    # Make a list of glyphs and number of anchor points
    AP_lst = []
    for glyph in font:
        AP_lst.append( [glyph, len(font[glyph].anchorPoints)] )
    # Sort by numb of APs then glyphname
    AP_lst.sort(AP_cmp)
    for AP in AP_lst:
        outf.write("%s,%s\n" % (AP[0], AP[1]))

    outf.close()
    print "done"

def AP_cmp(a, b): # Comparison to sort first by number of attachment points) then by Glyph name
    c = cmp(a[1], b[1])
    if c != 0:
        return c
    else:
        return cmp(a[0], b[0])

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
