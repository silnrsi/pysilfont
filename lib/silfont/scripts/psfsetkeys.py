#!/usr/bin/env python
'''Set keys with given values in a UFO plist file.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute
import codecs

suffix = "_setkeys"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('--plist',{'help': 'Select plist to modify'}, {'def': 'fontinfo'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': None}),
    ('-k','--key',{'help': 'Name of key to set'},{}),
    ('-v','--value',{'help': 'Value to set key to'},{}),
    ('--file',{'help': 'Use contents of file to set key to'},{}),
    ('--filepart',{'help': 'Use contents of part of the file to set key to'},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})
    ]

def doit(args) :

    # Determine which plist to modify
    if args.plist == 'lib':
        font_plist = args.ifont.lib
    else:
        font_plist = args.ifont.fontinfo

    # Ensure enough options were specified
    value = args.value or args.file or args.filepart
    if args.key and not value:
        args.logger.log('Value needs to be specified')
    if not args.key and value:
        args.logger.log('Key needs to be specified')

    # Use a one line string to set the key
    if args.key and args.value:
        set_key_value(font_plist, args.key, args.value)

    # Use entire file contents to set the key
    if args.key and args.file:
        fh = codecs.open(args.file, 'r', 'utf-8')
        contents = ''.join(fh.readlines())
        set_key_value(font_plist, args.key, contents)
        fh.close()

    # Use some of the file contents to set the key
    if args.key and args.filepart:
        fh = codecs.open(args.filepart, 'r', 'utf-8')
        lines = list()
        for line in fh:
            if line == '\n':
                break
            lines.append(line)
        contents = ''.join(lines)
        set_key_value(font_plist, args.key, contents)
        fh.close()

    # Set many keys
    if args.input:
        incsv = args.input
        incsv.numfields = 2
        incsv.logger = args.ifont.logger

        for line in incsv:
            key = line[0]
            value = line[1]
            set_key_value(font_plist, key, value)

    return args.ifont


def set_key_value(font_plist, key, value):
    """Set key to value in font."""

    # Currently setval() only works for integer, real or string.
    # For other items you need to construct an elementtree element and use setelem()

    value_type = 'string'

    # Handle boolean values
    if value == 'True':
        value_type = 'integer'
        value = 1
    if value == 'False':
        value_type = 'integer'
        value = 0

    font_plist.setval(key, value_type, value)


def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
