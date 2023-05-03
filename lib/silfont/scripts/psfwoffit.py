#!/usr/bin/env python
__doc__ = 'Convert font between ttf, woff, woff2'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.core import execute
from fontTools.ttLib import TTFont
from fontTools.ttLib.sfnt import WOFFFlavorData
from fontTools.ttLib.woff2 import WOFF2FlavorData
import os.path

argspec = [
    ('infont', {'help': 'Source font file (can be ttf, woff, or woff2)'}, {}),
    ('-m', '--metadata', {'help': 'file containing XML WOFF metadata', 'default': None}, {}),
    ('--privatedata', {'help': 'file containing WOFF privatedata', 'default': None}, {}),
    ('-v', '--version', {'help': 'woff font version number in major.minor', 'default': None}, {}),
    ('--ttf',   {'help': 'name of ttf file to be written',   'nargs': '?', 'default': None, 'const': '-'}, {}),
    ('--woff',  {'help': 'name of woff file to be written',  'nargs': '?', 'default': None, 'const': '-'}, {}),
    ('--woff2', {'help': 'name of woff2 file to be written', 'nargs': '?', 'default': None, 'const': '-'}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_woffit.log'})]

def doit(args):
    logger = args.logger
    infont = args.infont
    font = TTFont(args.infont)
    defaultpath = os.path.splitext(infont)[0]
    inFlavor = font.flavor or 'ttf'
    logger.log(f'input font {infont} is a {inFlavor}', 'I')

    # Read & parse version, if provided
    flavorData = WOFFFlavorData()  # Initializes all fields to None

    if args.version:
        try:
            version = float(args.version)
            if version < 0:
                raise ValueError('version cannot be negative')
            flavorData.majorVersion, flavorData.minorVersion = map(int, format(version, '.3f').split('.'))
        except:
            logger.log(f'invalid version syntax "{args.version}": should be MM.mmm', 'S')
    else:
        try:
            flavorData.majorVersion = font.flavorData.majorVersion
            flavorData.minorVersion = font.flavorData.minorVersion
        except:
            # Pull version from head table
            head = font['head']
            flavorData.majorVersion, flavorData.minorVersion =map(int, format(head.fontRevision, '.3f').split('.'))

    # Read metadata if provided, else get value from input font
    if args.metadata:
        try:
            with open(args.metadata, 'rb') as f:
                flavorData.metaData = f.read()
        except:
            logger.log(f'Unable to read file "{args.metadata}"', 'S')
    elif inFlavor != 'ttf':
        flavorData.metaData = font.flavorData.metaData

    # Same process for private data
    if args.privatedata:
        try:
            with open(args.privatedata, 'rb') as f:
                flavorData.privateData = f.read()
        except:
            logger.log(f'Unable to read file "{args.privatedata}"', 'S')
    elif inFlavor != 'ttf':
        flavorData.privData = font.flavorData.privData

    if args.woff:
        font.flavor = 'woff'
        font.flavorData = flavorData
        fname =  f'{defaultpath}.{font.flavor}' if args.woff2 == '-' else args.woff
        logger.log(f'Writing {font.flavor} font to "{fname}"', 'P')
        font.save(fname)

    if args.woff2:
        font.flavor = 'woff2'
        font.flavorData = WOFF2FlavorData(data=flavorData)
        fname =  f'{defaultpath}.{font.flavor}' if args.woff2 == '-' else args.woff2
        logger.log(f'Writing {font.flavor} font to "{fname}"', 'P')
        font.save(fname)

    if args.ttf:
        font.flavor = None
        font.flavorData = None
        fname =  f'{defaultpath}.ttf' if args.ttf == '-' else args.ttf
        logger.log(f'Writing ttf font to "{fname}"', 'P')
        font.save(fname)

    font.close()

def cmd() : execute('FT',doit, argspec)
if __name__ == "__main__": cmd()



