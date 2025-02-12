#!/usr/bin/env python3
__doc__ = '''Set keys with given values in a UFO plist file.'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute
from xml.etree import ElementTree as ET
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

    font = args.ifont
    logger = args.logger
    plist = args.plist
    if plist is None: plist = "fontinfo"
    if plist not in ("lib", "fontinfo"):
        logger.log("--plist must be either fontinfo or lib", "S")
    else:
        if plist not in font.__dict__: font.addfile(plist)
    logger.log("Adding keys to " + plist, "I")
    font_plist = getattr(font, plist)

    # Ensure enough options were specified
    value = args.value or args.file or args.filepart
    if args.key and not value:
        logger.log('Value needs to be specified', "S")
    if not args.key and value:
        logger.log('Key needs to be specified', "S")

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

        for line in incsv:
            key = line[0]
            value = line[1]
            set_key_value(font_plist, key, value)

    return font

def set_key_value(font_plist, key, value):
    """Set key to value in font."""

    # Currently setval() only works for integer, real or string.
    # For other items you need to construct an elementtree element and use setelem()

    if value == 'true' or value == 'false':
        # Handle boolean values
        font_plist.setelem(key, ET.Element(value))
    else:
        try:
            # Handle integers values
            number = int(value)
            font_plist.setval(key, 'integer', number)
        except ValueError:
            # Handle string (including multi-line strings) values
            font_plist.setval(key, 'string', value)
    font_plist.font.logger.log(key + " added, value: " + str(value), "I")

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
