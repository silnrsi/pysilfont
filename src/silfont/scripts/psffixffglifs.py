#!/usr/bin/env python3
__doc__ = '''Make changes needed to a UFO following processing by FontForge.
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_postff.log'})]

def doit(args) :

    font = args.ifont
    logger = args.logger

    advances_removed = 0
    unicodes_removed = 0
    for layer in font.layers:
        if layer.layername == "public.background":
            for g in layer:
                glyph = layer[g]
                # Remove advance and unicode fields from background layer
                # (FF currently copies some from default layer)
                if "advance" in glyph:
                    glyph.remove("advance")
                    advances_removed += 1
                    logger.log("Removed <advance> from " + g, "I")
                uc = glyph["unicode"]
                if uc != []:
                    while glyph["unicode"] != []: glyph.remove("unicode",0)
                    unicodes_removed += 1
                    logger.log("Removed unicode value(s) from " + g, "I")

    if advances_removed + unicodes_removed > 0 :
        logger.log("Advance removed from " + str(advances_removed) + " glyphs and unicode values(s) removed from "
                   + str(unicodes_removed) + " glyphs", "P")
    else:
        logger.log("No advances or unicodes removed from glyphs", "P")

    return args.ifont

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
