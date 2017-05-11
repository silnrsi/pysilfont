#!/usr/bin/env python
'For use with chaindemo.py'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_conv.log'})]

def doit(args) :
    f=args.ifont
    f.fontinfo["descender"][1].text = -400
    return args.ifont

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
