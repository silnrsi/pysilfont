#!/usr/bin/python3
__doc__ = 'Display name fields and other bits for linking fonts into families'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute
from fontTools.ttLib import TTFont

WINDOWS_ENGLISH_IDS = 3, 1, 0x409

FAMILY_RELATED_IDS = {
    1: 'Family',
    2: 'Subfamily',
    4: 'Full name',
    6: 'PostScript name',
    16: 'Typographic/Preferred family',
    17: 'Typographic/Preferred subfamily',
    21: 'WWS family',
    22: 'WWS subfamily',
}

argspec = [
    ('infont', {'help': 'TTF file'}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_namefields.log'}),
]


def doit(args):
    logger = args.logger
    width = max([len(name_id_name) for name_id_name in FAMILY_RELATED_IDS.values()]) + 1

    font = TTFont(args.infont)
    names(width, font)


def names(width, font):
    """Print various name table fields and other related data."""

    table = font['name']
    (platform_id, encoding_id, language_id) = WINDOWS_ENGLISH_IDS
    for name_id in sorted(FAMILY_RELATED_IDS.keys()):
        name_id_name = FAMILY_RELATED_IDS[name_id] + ':'
        record = table.getName(
            nameID=name_id,
            platformID=platform_id,
            platEncID=encoding_id,
            langID=language_id
        )
        if record:
            print(f'{name_id:2}: {name_id_name:{width}} {record}')


if __name__ == '__main__':
    execute('FT', doit, argspec)
