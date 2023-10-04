#!/usr/bin/env python3
__doc__ = '''Check that the ufos in a designspace file are interpolatable'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from fontParts.world import OpenFont
import fontTools.designspaceLib as DSD

argspec = [
    ('designspace', {'help': 'Design space file'}, {'type': 'filename'}),
    ('-l','--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_checkinterp.log'}),
    ]

def doit(args) :
    logger = args.logger

    ds = DSD.DesignSpaceDocument()
    ds.read(args.designspace)
    if len(ds.sources) == 1: logger.log("The design space file has only one source UFO", "S")

    # Find all the UFOs from the DS Sources.  Where there are more than 2, the primary one will be considered to be
    # the one where info copy="1" is set (as per psfsyncmasters).  If not set for any, use the first ufo.
    pufo = None
    otherfonts = {}
    for source in ds.sources:
        ufo = source.path
        try:
            font = OpenFont(ufo)
        except Exception as e:
            logger.log("Unable to open " + ufo, "S")
        if source.copyInfo:
            if pufo: logger.log('Multiple fonts with <info copy="1" />', "S")
            pufo = ufo
            pfont = font
        else:
            otherfonts[ufo] = font
    if pufo is None: # If we can't identify the primary font by conyInfo, just use the first one
        pufo = ds.sources[0].path
        pfont = otherfonts[pufo]
        del otherfonts[pufo]

    pinventory = set(glyph.name for glyph in pfont)
    
    for oufo in otherfonts:      
        logger.log(f'Comparing {pufo} with {oufo}', 'P')
        ofont = otherfonts[oufo]
        oinventory = set(glyph.name for glyph in ofont)
    
        if pinventory != oinventory:
            logger.log("The glyph inventories in the two UFOs differ", "E")
            for glyphn in sorted(pinventory - oinventory):
                logger.log(f'{glyphn} is only in {pufo}', "W")
            for glyphn in sorted(oinventory - pinventory):
                logger.log(f'{glyphn} is only in {oufo}', "W")
        else:
            logger.log("The UFOs have the same glyph inventories", "P")
        # Are glyphs compatible for interpolation
        incompatibles = {}
        for glyphn in pinventory & oinventory:
            compatible, report = pfont[glyphn].isCompatible(ofont[glyphn])
            if not compatible: incompatibles[glyphn] = report
        if incompatibles:
            logger.log(f'{len(incompatibles)} glyphs are not interpolatable', 'E')
            for glyphn in sorted(incompatibles):
                logger.log(f'{glyphn} is not interpolatable', 'W')
                logger.log(incompatibles[glyphn], "I")
            if logger.scrlevel == "W": logger.log("To see detailed reports run with scrlevel and/or loglevel set to I")
        else:
            logger.log("All the glyphs are interpolatable", "P")

def cmd() : execute(None,doit, argspec)
if __name__ == "__main__": cmd()
