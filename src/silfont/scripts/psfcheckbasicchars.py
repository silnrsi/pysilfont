#!/usr/bin/env python3
__doc__ = '''Checks a UFO for the presence of glyphs that represent the
Recommended characters for Non-Roman fonts and warns if any are missing.
https://scriptsource.org/entry/gg5wm9hhd3'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute
from silfont.util import required_chars

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-r', '--rtl', {'help': 'Also include characters just for RTL scripts', 'action': 'store_true'}, {}),
    ('-s', '--silpua', {'help': 'Also include characters in SIL PUA block', 'action': 'store_true'}, {}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_checkbasicchars.log'})]

def doit(args) :
    font = args.ifont
    logger = args.logger

    rationales = {
        "A": "in Codepage 1252",
        "B": "in MacRoman",
        "C": "for publishing",
        "D": "for Non-Roman fonts and publishing",
        "E": "by Google Fonts",
        "F": "by TeX for visible space",
        "G": "for encoding conversion utilities",
        "H": "in case Variation Sequences are defined in future",
        "I": "to detect byte order",
        "J": "to render combining marks in isolation",
        "K": "to view sidebearings for every glyph using these characters"}

    charsets = ["basic"]
    if args.rtl: charsets.append("rtl")
    if args.silpua: charsets.append("sil")

    req_chars = required_chars(charsets)

    glyphlist = font.deflayer.keys()

    for glyphn in glyphlist :
        glyph = font.deflayer[glyphn]
        if len(glyph["unicode"]) == 1 :
            unival = glyph["unicode"][0].hex
            if unival in req_chars:
                del req_chars[unival]

    cnt = len(req_chars)
    if cnt > 0:
        for usv in sorted(req_chars.keys()):
            item = req_chars[usv]
            psname = item["ps_name"]
            gname = item["glyph_name"]
            name = psname if psname == gname else psname + ", " + gname
            logger.log("U+" + usv + " from the " + item["sil_set"] +
                       " set has no representative glyph (" + name + ")", "W")
            logger.log("Rationale: This character is needed " + rationales[item["rationale"]], "I")
            if item["notes"]:
                logger.log(item["notes"], "I")
        logger.log("There are " + str(cnt) + " required characters missing", "E")

    return

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
