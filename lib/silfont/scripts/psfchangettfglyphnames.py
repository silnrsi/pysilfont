#!/usr/bin/env python
__doc__ = 'Rename the glyphs in a ttf file based on production names in a UFO'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Alan Ward'

# Rename the glyphs in a ttf file based on production names in a UFO
# using same technique as fontmake.
# Production names come from ufo.lib.public.postscriptNames according to ufo2ft comments
# but I don't know exactly where in the UFO that is

from silfont.core import execute
import defcon, fontTools.ttLib, ufo2ft

argspec = [
    ('iufo', {'help': 'Input UFO folder'}, {}),
    ('ittf', {'help': 'Input ttf file name'}, {}), 
    ('ottf', {'help': 'Output ttf file name'}, {})]
    
def doit(args):
    ufo = defcon.Font(args.iufo)
    ttf = fontTools.ttLib.TTFont(args.ittf)
    
    args.logger.log('Renaming the input ttf glyphs based on production names in the UFO', 'P')
    postProcessor = ufo2ft.PostProcessor(ttf, ufo)
    ttf = postProcessor.process(useProductionNames=True, optimizeCFF=False)
    
    args.logger.log('Saving the output ttf file', 'P')
    ttf.save(args.ottf)
    
    args.logger.log('Done', 'P')

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
