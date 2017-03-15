#!/usr/bin/env python
''' Demon of how to chain calls to multple scripts together.
If chaintest1.py and chaintest2.py are installed from lib/silfont/scripts this will run execute() against
UFOconvert, chaintest1 and chaintest2 passing the font, parameters and logger objects from one call to the next.
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

import sys
import silfont.scripts.UFOconvert as UFOconvert
import dwr4 as dwr
import dwr5 as dwr2
from silfont.core import execute, chain

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_chain.log'})]

def doit(args) :

    argv = ['UFOconvert', 'dummy'] # 'dummy' replaces input font since font object is being passed.  Other paraeters could be added.
    font = chain(argv, UFOconvert.doit, UFOconvert.argspec, args.ifont, args.paramsobj, args.logger, args.quiet)

    argv = ['chaintest1', 'dummy']
    font = chain(argv, chaintest1.doit, chaintest1.argspec, font,       args.paramsobj, args.logger, args.quiet)

    argv = ['chaintest2', 'dummy']
    font = chain(argv, chaintest2.doit, chaintest2.argspec, font,       args.paramsobj, args.logger, args.quiet)

    return font

def cmd() : execute("UFO",doit, argspec)

if __name__ == "__main__": cmd()

