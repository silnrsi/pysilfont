#!/usr/bin/env python3
__doc__ = ''' Sets the cell mark color of glyphs in a UFO
- Input file is a list of glyph names (or unicode values if -u is specified
- Color can be numeric or certain names, eg "0.85,0.26,0.06,1" or "g_red"
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, splitfn
from silfont.util import parsecolors
import io

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'input file'}, {'type': 'filename', 'def': 'nodefault.txt'}),
    ('-c','--color',{'help': 'Color to set'},{}),
    ('-u','--unicodes',{'help': 'Use unicode values in input file', 'action': 'store_true', 'default': False},{}),
    ('-x','--deletecolors',{'help': 'Delete existing mark colors', 'action': 'store_true', 'default': False},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_setmarkcolors.log'})]

def doit(args) :
    font = args.ifont
    logger = args.logger
    infile = args.input
    color = args.color
    unicodes = args.unicodes
    deletecolors = args.deletecolors

    if not ((color is not None) ^ deletecolors): logger.log("Must specify one and only one of -c and -x", "S")

    if color is not None:
        (color, colorname, logcolor, splitcolor) = parsecolors(color, single=True)
        if color is None: logger.log(logcolor, "S") # If color not parsed, parsecolors() puts error in logcolor

    # Process the input file.  It needs to be done in script rather than by execute() since, if -x is used, there might not be one
    (ibase, iname, iext) = splitfn(infile)
    if iname == "nodefault": # Indicates no file was specified
        infile = None
        if (color is not None) or unicodes or (not deletecolors): logger.log("If no input file, -x must be used and neither -c or -u can be used", "S")
    else:
        logger.log('Opening file for input: ' + infile, "P")
        try:
            infile = io.open(infile, "r", encoding="utf-8")
        except Exception as e:
            logger.log("Failed to open file: " + str(e), "S")

    # Create list of glyphs to process
    if deletecolors and infile is None: # Need to delete colors from all glyphs
        glyphlist = sorted(font.deflayer.keys())
    else:
        inlist = [x.strip() for x in infile.readlines()]
        glyphlist = []
        if unicodes:
            unicodesfound = []
            for glyphn in sorted(font.deflayer.keys()):
                glyph = font.deflayer[glyphn]
                for unicode in [x.hex for x in glyph["unicode"]]:
                    if unicode in inlist:
                        glyphlist.append(glyphn)
                        unicodesfound.append(unicode)
            for unicode in inlist:
                if unicode not in unicodesfound: logger.log("No glyphs with unicode '" + unicode + "' in the font", "I")
        else:
            for glyphn in inlist:
                if glyphn in font.deflayer:
                    glyphlist.append(glyphn)
                else:
                    logger.log(glyphn + " is not in the font", "I")

    changecnt = 0
    for glyphn in glyphlist:
        glyph = font.deflayer[glyphn]
        oldcolor = None
        lib = glyph["lib"]
        if lib:
            if "public.markColor" in lib: oldcolor = str(glyph["lib"].getval("public.markColor"))
        if oldcolor != color:
            if oldcolor is not None:
                (temp, oldname, oldlogcolor, splitcolor) = parsecolors(oldcolor, single=True)
                if temp is None: oldlogcolor = oldcolor # Failed to parse old color, so just report what is was

            changecnt += 1
            if deletecolors:
                glyph["lib"].remove("public.markColor")
                logger.log(glyphn + ": " + oldlogcolor + " removed", "I")
            else:
                if oldcolor is None:
                    if lib is None: glyph.add("lib")
                    glyph["lib"].setval("public.markColor","string",color)
                    logger.log(glyphn+ ": " + logcolor + " added", "I")
                else:
                    glyph["lib"].setval("public.markColor", "string", color)
                    logger.log(glyphn + ": " + oldlogcolor + " changed to " + logcolor, "I")

    if deletecolors:
        logger.log(str(changecnt) + " colors removed", "P")
    else:
        logger.log(str(changecnt) + " colors changed or added", "P")

    return font

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
