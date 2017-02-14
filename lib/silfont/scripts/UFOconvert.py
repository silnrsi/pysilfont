#!/usr/bin/env python
'''Convert/normalise a UFO.
- If no options are chosen, the output font will simply be a normalised version of the font.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_conv.log'})]

def doit(args) :
    return args.ifont

def cmd() : execute("PSFU",doit, argspec)

if __name__ == "__main__": cmd()
