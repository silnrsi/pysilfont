#!/usr/bin/python3
__doc__ = 'Display name fields and other bits for linking fonts into families'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute, splitfn
from fontTools.ttLib import TTFont
import glob

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
    ('fonts', {'help': 'ttf font(s) to run report against; wildcards allowed', 'nargs': "+"}, {'type': 'filename'})
]


def doit(args):
    logger = args.logger
    name_width = max([len(name_id_name) for name_id_name in FAMILY_RELATED_IDS.values()]) + 1

    fonts = []
    filename_width = 0
    for pattern in args.fonts:
        for fullpath in glob.glob(pattern):
            (path, base, ext) = splitfn(fullpath)
            filename_width = max(filename_width, len(fullpath)+1)
            fonts.append((fullpath, path, base, ext))
    if fonts == []:
        logger.log("No files match the filespec provided for fonts: " + str(args.fonts), "S")

    for (fullpath, path, base, ext) in fonts:
        logger.log(f'Processing {fullpath}', 'P')
        try:
            font = TTFont(fullpath)
        except Exception as e:
            logger.log(f'Error opening {fullpath}: {e}', 'E')
            break

        filename = ''
        if len(fonts) > 1:
            filename = fullpath + ':'
            filename = f'{filename:{filename_width}} '
        records = names(name_width, font, filename)
        if args.quiet:
            print(records[1:])
        else:
            logger.log("The following family-related values were found in the name table" + records, "P")


def names(name_width, font, filename):
    table = font['name']
    (platform_id, encoding_id, language_id) = WINDOWS_ENGLISH_IDS

    records = ''
    for name_id in sorted(FAMILY_RELATED_IDS.keys()):
        name_id_name = FAMILY_RELATED_IDS[name_id] + ':'
        record = table.getName(
            nameID=name_id,
            platformID=platform_id,
            platEncID=encoding_id,
            langID=language_id
        )
        if record:
            records += f'\n{filename}{name_id:2}: {name_id_name:{name_width}} {record}'

    return records


def cmd(): execute('FT', doit, argspec)


if __name__ == '__main__':
    cmd()
