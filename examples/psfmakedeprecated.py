#!/usr/bin/env python3
'''Creates deprecated versions of glyphs: takes the specified glyph and creates a
duplicate with an additional box surrounding it so that it becomes reversed, 
and assigns a new unicode encoding to it.
Input is a csv with three fields: original,new,unicode'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute
from fontParts.world import *

# Setting input - Note that for fontParts you specify filenames for 
# input and output rather than infont or outfont. This script writes
# changes back to the original font.
argspec = [
    ('ifont', {'help': 'Input font filename'}, {'type': 'filename'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': 'todeprecate.csv'}),
    ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': '_deprecated.log'})]

offset = 30

def doit(args) :
    font = OpenFont(args.ifont)
    logger = args.logger

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
            
            # Draw box around it
            xmin, ymin, xmax, ymax = sourceglyph.bounds
            pen = newglyph.getPen()
            pen.moveTo((xmax + offset, ymin - offset))
            pen.lineTo((xmax + offset, ymax + offset))
            pen.lineTo((xmin - offset, ymax + offset))
            pen.lineTo((xmin - offset, ymin - offset))
            pen.closePath()

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
    
    # Write the changes to a font directly rather than returning an object
    font.save()

    return

# Note the use of None rather than "UFO" in this execute()
def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
