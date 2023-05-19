#!/usr/bin/env python3
__doc__ = '''Set the unicodes of glyphs in a font based on an external csv file.
- csv format glyphname,unicode, [unicode2, [,unicode3]]'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney, based on UFOsetPSnames.py'

from silfont.core import execute

suffix = "_setunicodes"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})]

def doit(args) :
    font = args.ifont
    incsv = args.input
    logger = args.logger
    # Allow for up to 3 unicode values per glyph
    incsv.minfields = 2
    incsv.maxfields = 4

    # List of glyphnames actually in the font:
    glyphlist = list(font.deflayer.keys())

    # Create mapping to find glyph name from decimal usv:
    dusv2gname = {int(unicode.hex, 16): gname for gname in glyphlist for unicode in font.deflayer[gname]['unicode']}

    # Remember what glyphnames we've processed:
    processed = set()

    for line in incsv :
        glyphn = line[0]
        # Allow for up to 3 unicode values
        dusvs = []
        for col in range(1,len(line)):
            try:
                dusv = int(line[col],16)  # sanity check and convert to decimal
            except ValueError:
                logger.log("Invalid USV '%s'; line %d ignored." % (line[col], incsv.line_num), "W")
                continue
            dusvs.append(dusv)

        if glyphn in glyphlist :

            if glyphn in processed:
                logger.log(f"Glyph {glyphn} in csv more than once; line {incsv.line_num} ignored.", "W")

            glyph = font.deflayer[glyphn]
            # Remove existing unicodes
            for unicode in list(glyph["unicode"]):
                del dusv2gname[int(unicode.hex, 16)]
                glyph.remove("unicode",index = 0)

            # Add the new unicode(s) in
            for dusv in dusvs:
                # See if any glyph already encodes this unicode value:
                if dusv in dusv2gname:
                    # Remove this encoding from the other glyph:
                    oglyph = font.deflayer[dusv2gname[dusv]]
                    for unicode in oglyph["unicode"]:
                        if int(unicode.hex,16) == dusv:
                            oglyph.remove("unicode", object=unicode)
                            break
                # Add this unicode value and update dusv2gname
                dusv2gname[dusv] = glyphn
                glyph.add("unicode",{"hex": ("%04X" % dusv)})  # Standardize to 4 (or more) digits and caps
            # Record that we processed this glyphname,
            processed.add(glyphn)
        else :
            logger.log("Glyph '%s' not in font; line %d ignored." % (glyphn, incsv.line_num), "I")

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
