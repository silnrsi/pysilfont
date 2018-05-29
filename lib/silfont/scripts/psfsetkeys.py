#!/usr/bin/env python
'''Set key with given values in a UFO fontinfo.plist file.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_setkey.log'}),
    ('-k','--key',{'help': 'name of key to set'},{}),
    ('-v','--value',{'help': 'value to set key to'},{})
    ]

def doit(args) :

    # Currently setval() only works for integer, real or string.
    # For other items you need to construct an elementtree element and use setelem()
    if args.key and args.value:
        args.ifont.fontinfo.setval(args.key, 'string', args.value)
    else:
        args.logger.log('Both key and value need to be specified')

    return args.ifont

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
