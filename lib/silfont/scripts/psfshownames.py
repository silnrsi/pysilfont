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


class FontInfo:
    def __init__(self):
        self.filename = ''
        self.name_table = dict()
        self.weight_class = 0
        self.regular = ''
        self.bold = ''
        self.italic = ''
        self.width = ''
        self.width_name = ''
        self.width_class = 0
        self.wws = ''


argspec = [
    ('font', {'help': 'ttf font(s) to run report against; wildcards allowed', 'nargs': "+"}, {'type': 'filename'}),
    ('-b', '--bits', {'help': 'Show bits', 'action': 'store_true'}, {}),
]


def doit(args):
    logger = args.logger
    name_width = max([len(name_id_name) for name_id_name in FAMILY_RELATED_IDS.values()]) + 1

    fonts = []
    font_infos = []
    filename_width = 0
    for pattern in args.font:
        for fullpath in glob.glob(pattern):
            (path, base, ext) = splitfn(fullpath)
            filename_width = max(filename_width, len(fullpath) + 1)
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

        font_info = FontInfo()
        font_info.filename = fullpath
        names(font, font_info)
        bits(font, font_info)
        font_infos.append(font_info)

    for font_info in font_infos:
        filename = ''
        if len(font_infos) > 1:
            filename = font_info.filename + ':'
            filename = f'{filename:{filename_width}} '
        records = multiline_names(name_width, font_info, filename)
        if args.bits:
            records += multiline_bits(name_width, font_info, filename)
        if args.quiet:
            print(records[1:])
        else:
            logger.log("The following family-related values were found in the name, head, and OS/2 tables" + records, "P")


def names(font, font_info):
    table = font['name']
    (platform_id, encoding_id, language_id) = WINDOWS_ENGLISH_IDS

    for name_id in FAMILY_RELATED_IDS:
        record = table.getName(
            nameID=name_id,
            platformID=platform_id,
            platEncID=encoding_id,
            langID=language_id
        )
        if record:
            font_info.name_table[name_id] = str(record)


def bits(font, font_info):
    os2 = font['OS/2']
    head = font['head']
    font_info.weight_class = os2.usWeightClass
    font_info.regular = bit2code(os2.fsSelection, 6, 'W-')
    font_info.bold = bit2code(os2.fsSelection, 5, 'W')
    font_info.bold += bit2code(head.macStyle, 0, 'M')
    font_info.italic = bit2code(os2.fsSelection, 0, 'W')
    font_info.italic += bit2code(head.macStyle, 1, 'M')
    font_info.width_class = os2.usWidthClass
    font_info.width = str(font_info.width_class)
    if font_info.width_class == 5:
        font_info.width_name = 'Width-Normal'
    if font_info.width_class < 5:
        font_info.width_name = 'Width-Condensed'
        font_info.width += bit2code(head.macStyle, 5, 'M')
    if font_info.width_class > 5:
        font_info.width_name = 'Width-Extended'
        font_info.width += bit2code(head.macStyle, 6, 'M')
    font_info.wws = bit2code(os2.fsSelection, 8, '8')


def multiline_names(name_width, font_info, filename):
    records = ''
    for name_id in sorted(font_info.name_table):
        name_id_name = FAMILY_RELATED_IDS[name_id] + ':'
        record = font_info.name_table[name_id]
        records += f'\n{filename}{name_id:2}: {name_id_name:{name_width}} {record}'
    return records


def multiline_bits(name_width, font_info, filename):
    records = ''
    records += bit_record(filename, 'usWeightClass', name_width, font_info.weight_class)
    records += bit_record(filename, 'Regular', name_width, font_info.regular)
    records += bit_record(filename, 'Bold', name_width, font_info.bold)
    records += bit_record(filename, 'Italic', name_width, font_info.italic)
    records += bit_record(filename, font_info.width_name, name_width, font_info.width)
    records += bit_record(filename, 'WWS', name_width, font_info.wws)
    return records


def bit2code(bit_field, bit, code_letter):
    code = ''
    if bit_field & 1 << bit:
        code = code_letter
    return code


def bit_record(filename, bit_field_name, name_width, codes):
    if codes:
        bit_field_name += ':'
        record = f'\n{filename}    {bit_field_name:{name_width}} {codes}'
        return record
    return ''


def cmd(): execute('FT', doit, argspec)


if __name__ == '__main__':
    cmd()
