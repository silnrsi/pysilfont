#!/usr/bin/env python
'''FontForge: Double encode glyphs based on double encoding data in a file
Lines in file should look like: "LtnSmARetrHook",U+F236,U+1D8F'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('-i','--input',{'help': 'Input csv text file'}, {'type': 'infile', 'def': 'DblEnc.txt'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'DblEnc.log'})]

def doit(args) :
    font = args.ifont
    inpf = args.input
    logf = args.log
#Create dbl_encode list from the input file
    dbl_encode = {}
    for line in inpf.readlines() :
        glyphn, pua_usv_str, std_usv_str = line.strip().split(",")  # will exception if not 3 elements
        if glyphn[0] in '"\'' : glyphn = glyphn[1:-1]               # slice off quote marks, if present
        pua_usv, std_usv = int(pua_usv_str[2:], 16), int(std_usv_str[2:], 16)
        dbl_encode[glyphn] = [std_usv, pua_usv]
    inpf.close()

    for glyph in sorted(dbl_encode.keys()) :
        if glyph not in font:
            logf.write("Glyph %s not in font\n" % (glyph))
            continue
        g = font[glyph]
        ousvs=[g.unicode]
        oalt=g.altuni
        if oalt != None:
            for au in oalt:
                ousvs.append(au[0]) # (may need to check variant flag)
        dbl = dbl_encode[glyph]
        g.unicode = dbl[0]
        g.altuni = ((dbl[1],),)
        logf.write("encoding for %s changed: %s -> %s\n" % (glyph, ousvs, dbl))
    logf.close()
    return font

execute("FF",doit, argspec)
