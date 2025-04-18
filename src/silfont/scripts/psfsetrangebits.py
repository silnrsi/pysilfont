#!/usr/bin/env python3
__doc__ = '''Set Unicode and/or Codepage range bits in UFO'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy`'

from silfont.core import execute
import re

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-c','--codepage', {'help': 'OS/2 range bit data'}, {}),
    ('-u','--unicode',{'help': 'OS/2 range bit data'}, {}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_rangebits.log'}),
    ]

def getBitNums(s):
    if m := re.match(r'[0-9a-fA-F]+$', s):
        bitnums = []
        startnum = len(s)*4-1
        for hexdigit in s:
            bits = bin(int(hexdigit,16))[2:].zfill(4)
            bitnums.extend([startnum-i for i in range(0,4) if bits[i]=='1'])
            startnum -= 4
    elif re.match(r'\d+(,\d+)*$', s):
        bitnums = list(set([int(i) for i in s.split(',')]))
    else:
        return None
    return sorted(bitnums)


def doit(args) :
    if not (args.codepage or args.unicode):
        args.logger.log('At least one of --codepage or --unicode must be provided', 'S')

    haserrors = False
    font = args.ifont
    fontinfo = font.info.naked()

    if args.unicode:
        bitnums = getBitNums(args.unicode)
        if bitnums is None:
            args.logger.log(f'-u parameter "{args.unicode}" cannot be interpreted', 'E')
            haserrors = True
        else:
            fontinfo.openTypeOS2UnicodeRanges = bitnums
            args.logger.log(f'changed Unicode range bits to {bitnums}', 'P')
    
    if args.codepage:
        bitnums = getBitNums(args.codepage)
        if bitnums is None:
            args.logger.log(f'-c parameter "{args.codepage}" cannot be interpreted', 'E')
            haserrors = True
        else:
            fontinfo.openTypeOS2CodePageRanges = bitnums
            args.logger.log(f'changed codepage range bits to {bitnums}', 'P')
    
    if haserrors:
        return()
    font.info.changed()
    return(font)


def cmd() : execute('FP',doit, argspec)
if __name__ == "__main__": cmd()