#!/usr/bin/env python
__doc__ = ''' Sets the cell mark color of glyphs in a UFO
- Input file is a list of glpyh names (or unicode values if -u is specified
- Color can be numeric or certain names, eg "0.85,0.26,0.06,1" or "g_red"
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, splitfn
from silfont.util import nametocolor, colortoname
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
        if color[0] not in ("0", "1"):
            color = nametocolor(color, "")
            if color == "" : logger.log("Invalid color name", "S")

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
                if unicode not in unicodesfound: logger.log("No gylphs with unicode '" + unicode + "' in the font", "I")
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
            changecnt += 1
            if deletecolors:
                glyph["lib"].remove("public.markColor")
                logger.log(glyphn + ": " + logcolor(oldcolor) + " removed", "I")
            else:
                if oldcolor is None:
                    if lib is None: glyph.add("lib")
                    glyph["lib"].setval("public.markColor","string",color)
                    logger.log(glyphn+ ": " + logcolor(color) + " added", "I")
                else:
                    glyph["lib"].setval("public.markColor", "string", color)
                    logger.log(glyphn + ": " + logcolor(oldcolor) + " changed to " + logcolor(color), "I")

    if deletecolors:
        logger.log(str(changecnt) + " colors removed", "P")
    else:
        logger.log(str(changecnt) + " colors changed or added", "P")

    return font

def logcolor(color): # Add color name, if there is one, to color for logging
    colorname = colortoname(color)
    if colorname is not None: color = color + " (" + colorname + ")"
    return color


def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
