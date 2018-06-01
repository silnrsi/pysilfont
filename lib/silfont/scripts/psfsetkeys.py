#!/usr/bin/env python
'''Set keys with given values in a UFO fontinfo.plist file.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute

suffix = "_setkeys"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('--plist',{'help': 'Select plist to modify'}, {'def': 'fontinfo'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': None}),
    ('-k','--key',{'help': 'Name of key to set'},{}),
    ('-v','--value',{'help': 'Value to set key to'},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})
    ]

def doit(args) :

    # Currently setval() only works for integer, real or string.
    # For other items you need to construct an elementtree element and use setelem()

    # Determine which plist to modify
    if args.plist == 'lib':
        font_plist = args.ifont.lib
    else:
        font_plist = args.ifont.fontinfo

    # Set one key
    if args.key and not args.value:
        args.logger.log('Value needs to be specified')
    if not args.key and args.value:
        args.logger.log('Key needs to be specified')
    if args.key and args.value:
        font_plist.setval(args.key, 'string', args.value)

    # Set many keys
    if args.input:
        incsv = args.input
        incsv.numfields = 2
        incsv.logger = args.ifont.logger

        for line in incsv:
            key = line[0]
            value = line[1]
            font_plist.setval(key, 'string', value)

    return args.ifont

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
