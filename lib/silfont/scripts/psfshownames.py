#!/usr/bin/python3
__doc__ = 'Display name fields and other bits for linking fonts into families'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute, splitfn
from fontTools.ttLib import TTFont
import glob
import tabulate

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
    ('-m', '--multiline', {'help': 'Output multi-line key:values instead of a table', 'action': 'store_true'}, {}),
]


def doit(args):
    logger = args.logger

    font_infos = []
    filename_width = 0
    for pattern in args.font:
        for fullpath in glob.glob(pattern):
            logger.log(f'Processing {fullpath}', 'P')
            try:
                font = TTFont(fullpath)
            except Exception as e:
                logger.log(f'Error opening {fullpath}: {e}', 'E')
                break

            font_info = FontInfo()
            font_info.filename = fullpath
            get_names(font, font_info)
            get_bits(font, font_info)
            font_infos.append(font_info)

            # Only needed for multi-line mode
            filename_width = max(filename_width, len(fullpath) + 1)

    if not font_infos:
        logger.log("No files match the filespec provided for fonts: " + str(args.fonts), "S")

    if args.multiline:
        # Multi-line mode
        name_width = max([len(name_id_name) for name_id_name in FAMILY_RELATED_IDS.values()]) + 1
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
    else:
        # Table mode

        # Record information for headers
        headers = table_headers(args.bits)

        # Record information for each instance.
        records = list()
        for font_info in font_infos:
            record = table_records(font_info, args.bits)
            records.append(record)

        # Not all fonts in a family with have the same name ids present,
        # for instance 16: Typographic/Preferred family is only needed in
        # non-RIBBI familes, and even then only for the non-RIBBI instances.
        # Also, not all the bit fields are present in each instance.
        # Therefore, columns with no data in any instance are removed.
        indices = list(range(len(headers)))
        indices.reverse()
        for index in indices:
            empty = True
            for record in records:
                data = record[index]
                if data:
                    empty = False
            if empty:
                for record in records + [headers]:
                    del record[index]

        # Format 'pipe' is nicer for GitHub, but is wider on a command line
        print(tabulate.tabulate(records, headers, tablefmt='simple'))


def get_names(font, font_info):
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


def get_bits(font, font_info):
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


def bit2code(bit_field, bit, code_letter):
    code = ''
    if bit_field & 1 << bit:
        code = code_letter
    return code


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


def bit_record(filename, bit_field_name, name_width, codes):
    if codes:
        bit_field_name += ':'
        record = f'\n{filename}    {bit_field_name:{name_width}} {codes}'
        return record
    return ''


def table_headers(bits):
    headers = ['filename']
    for name_id in sorted(FAMILY_RELATED_IDS):
        name_id_key = FAMILY_RELATED_IDS[name_id]
        header = f'{name_id}: {name_id_key}'
        if len(header) > 20:
            header = header.replace(' ', '\n')
            header = header.replace('/', '\n')
        headers.append(header)
    if bits:
        headers.extend(['wght', 'R', 'B', 'I', 'wdth', 'WWS'])
    return headers


def table_records(font_info, bits):
    record = [font_info.filename]
    for name_id in sorted(FAMILY_RELATED_IDS):
        name_id_value = font_info.name_table.get(name_id, '')
        record.append(name_id_value)
    if bits:
        record.append(font_info.weight_class)
        record.append(font_info.regular)
        record.append(font_info.bold)
        record.append(font_info.italic)
        record.append(font_info.width)
        record.append(font_info.wws)
    return record


def cmd(): execute('FT', doit, argspec)


if __name__ == '__main__':
    cmd()
