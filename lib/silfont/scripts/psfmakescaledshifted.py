#!/usr/bin/env python3
'''Creates duplicate versions of glyphs that are scaled and shifted.
Input is a csv with three fields: original,new,unicode'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute
from ast import literal_eval as make_tuple

argspec = [
    ('ifont', {'help': 'Input font filename'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': 'todeprecate.csv'}),
    ('-t','--transform',{'help': 'Transform matrix'}, {}),
    ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': '_deprecated.log'})]

offset = 30

def doit(args) :
    font = args.ifont
    logger = args.logger
    trans = make_tuple(args.transform)
    #trans = make_tuple("(0.72, 0, 0, 0.6, 10, 806)")

    # Process csv list into a dictionary structure
    args.input.numfields = 3
    deps = {}
    for line in args.input :
        deps[line[0]] = {"newname": line[1], "newuni": line[2]}

    # Iterate through dictionary (unsorted)
    for source, target in deps.items() :
        # Check if source glyph is in font
        if source in font.keys() :
            # Give warning if target is already in font, but overwrite anyway
            targetname = target["newname"]
            targetuni = int(target["newuni"], 16)
            if targetname in font.keys() :
                logger.log("Warning: " + targetname + " already in font and will be replaced")

            # Make a copy of source into a new glyph object
            sourceglyph = font[source]            
            newglyph = sourceglyph.copy()
            
            # obj.transformBy((0.5, 0, 0, 2.0, 10, 0))
            newglyph.transformBy(trans)
            # Set width because transformBy does not seems to properly adjust width
            newglyph.width = (int(newglyph.width * trans[0])) + trans[4]

            # Set unicode
            newglyph.unicodes = []
            newglyph.unicode = targetuni

            # Add the new glyph object to the font with name target
            font.__setitem__(targetname,newglyph)

            # Decompose glyph in case there may be components
            # It seems you can't decompose a glyph has hasn't yet been added to a font
            font[targetname].decompose()
            # Correct path direction            
            font[targetname].correctDirection()            

            logger.log(source + " duplicated to " + targetname)
        else :
            logger.log("Warning: " + source + " not in font")

    return font

def cmd() : execute("FP",doit,argspec)
if __name__ == "__main__": cmd()
