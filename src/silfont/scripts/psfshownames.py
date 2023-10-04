#!/usr/bin/env python3
__doc__ = 'Display name fields and other bits for linking fonts into families'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute, splitfn
from fontTools.ttLib import TTFont
import glob
from operator import attrgetter, methodcaller
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
    25: 'Variations PostScript Name Prefix',
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

    def sort_fullname(self):
        return self.name_table[4]


argspec = [
    ('font', {'help': 'ttf font(s) to run report against; wildcards allowed', 'nargs': "+"}, {'type': 'filename'}),
    ('-b', '--bits', {'help': 'Show bits', 'action': 'store_true'}, {}),
    ('-m', '--multiline', {'help': 'Output multi-line key:values instead of a table', 'action': 'store_true'}, {}),
]


def doit(args):
    logger = args.logger

    font_infos = []
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

    if not font_infos:
        logger.log("No files match the filespec provided for fonts: " + str(args.font), "S")

    font_infos.sort(key=methodcaller('sort_fullname'))
    font_infos.sort(key=attrgetter('width_class'), reverse=True)
    font_infos.sort(key=attrgetter('weight_class'))

    rows = list()
    if args.multiline:
        # Multi-line mode
        for font_info in font_infos:
            for line in multiline_names(font_info):
                rows.append(line)
            if args.bits:
                for line in multiline_bits(font_info):
                    rows.append(line)
        align = ['left', 'right']
        if len(font_infos) == 1:
            del align[0]
            for row in rows:
                del row[0]
        output = tabulate.tabulate(rows, tablefmt='plain', colalign=align)
        output = output.replace(': ', ':')
        output = output.replace('#', '')
    else:
        # Table mode

        # Record information for headers
        headers = table_headers(args.bits)

        # Record information for each instance.
        for font_info in font_infos:
            record = table_records(font_info, args.bits)
            rows.append(record)

        # Not all fonts in a family with have the same name ids present,
        # for instance 16: Typographic/Preferred family is only needed in
        # non-RIBBI families, and even then only for the non-RIBBI instances.
        # Also, not all the bit fields are present in each instance.
        # Therefore, columns with no data in any instance are removed.
        indices = list(range(len(headers)))
        indices.reverse()
        for index in indices:
            empty = True
            for row in rows:
                data = row[index]
                if data:
                    empty = False
            if empty:
                for row in rows + [headers]:
                    del row[index]

        # Format 'pipe' is nicer for GitHub, but is wider on a command line
        output = tabulate.tabulate(rows, headers, tablefmt='simple')

    # Print output from either mode
    if args.quiet:
        print(output)
    else:
        logger.log('The following family-related values were found in the name, head, and OS/2 tables\n' + output, 'P')


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


def multiline_names(font_info):
    for name_id in sorted(font_info.name_table):
        line = [font_info.filename + ':',
                str(name_id) + ':',
                FAMILY_RELATED_IDS[name_id] + ':',
                font_info.name_table[name_id]
                ]
        yield line


def multiline_bits(font_info):
    labels = ('usWeightClass', 'Regular', 'Bold', 'Italic', font_info.width_name, 'WWS')
    values = (font_info.weight_class, font_info.regular, font_info.bold, font_info.italic, font_info.width, font_info.wws)
    for label, value in zip(labels, values):
        if not value:
            continue
        line = [font_info.filename + ':',
                '#',
                str(label) + ':',
                value
                ]
        yield line


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
