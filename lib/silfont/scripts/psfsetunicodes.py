#!/usr/bin/env python
'''Set the unicodes of glyphs in a font based on an external file. Note that this will not currently remove any unicode values that already exist in unlisted glyphs
- csv format glyphname,unicode'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney, based on UFOsetPSnames.py'

from silfont.core import execute

suffix = "_updated"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})]

def doit(args) :
    font = args.ifont
    incsv = args.input
    logger = args.logger
    
    # Identify file format from first line
    fl = incsv.firstline
    if fl is None: logger.log("Empty imput file", "S")
    numfields = len(fl)
    if numfields == 2 and 'glyph_name' not in fl:
        nameCol = 0       # Defaults for plain csv
        usvCol = 1
    elif numfields >= 2:  # Must have headers
        # required columns:
        try:
            nameCol = fl.index('glyph_name');
            usvCol = fl.index('USV')
            next(incsv.reader, None)  # Skip first line with headers in
        except ValueError as e:
            logger.log('Missing csv input field: ' + e.message, 'S')
        except Exception as e:
            logger.log('Error reading csv input field: ' + e.message, 'S')
    else:
        logger.log("Invalid csv file", "S")

    # List of glyphnames actually in the font:
    glyphlist = list(font.deflayer.keys())

    # Create mapping to find glyph name from decimal usv:
    dusv2gname = {int(unicode.hex, 16): gname for gname in glyphlist for unicode in font.deflayer[gname]['unicode']}

    # Remember what glyphnames we've processed:
    processed = set()

    for line in incsv :
        glyphn = line[nameCol]
        try:
            dusv = int(line[usvCol],16)  # sanity check and convert to decimal
        except ValueError:
            logger.log("Invalid USV '%s'; line %d ignored." % (line[usvCol], incsv.line_num), "W")
            continue
        unival = "%04X" % dusv  # Standardize to 4 (or more) digits and caps

        if glyphn in glyphlist :
            glyph = font.deflayer[glyphn]

            # If this is the first time we've seen this glyphname and there is only one unicode value on this glyph, assume we are replacing it.
            if glyphn not in processed and len(glyph["unicode"]) == 1 :
                del dusv2gname[int(glyph["unicode"][0].hex, 16)]
                glyph.remove("unicode",index = 0)

            # See if any glyph already encodes this unicode value:
            if dusv in dusv2gname:
                # Yes ... some glyph does.
                if dusv2gname[dusv] == glyphn:
                    # Oh, it's me!  Do nothing except remember we processed this glyph:
                    processed.add(glyphn)
                    continue
                # Not me, so remove this encoding from the other glyph:
                oglyph = font.deflayer[dusv2gname[dusv]]
                for unicode in oglyph["unicode"]:
                    if int(unicode.hex,16) == dusv:
                        oglyph.remove("unicode", object=unicode)
                        break

            # Finally add this unicode value, record that we processed this glyphname, and update dusv2gname
            glyph.add("unicode",{"hex": unival})
            processed.add(glyphn)
            dusv2gname[dusv] = glyphn
        else :
            logger.log("Glyph '%s' not in font; line %d ignored." % (glyphn, incsv.line_num), "I")

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
