#!/usr/bin/env python3
__doc__ = '''Set keys with given values in a UFO plist file.'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute
from xml.etree import ElementTree as ET
import codecs
import re

suffix = "_setkeys"
argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont', {'help': 'Output font file', 'nargs': '?'}, {'type': 'outfont'}),
    ('--plist', {'help': 'Select plist to modify'}, {'def': 'fontinfo'}),
    ('-i', '--input', {'help': 'Input csv file'}, {'type': 'incsv', 'def': None}),
    ('-k', '--key', {'help': 'Name of key to set'}, {}),
    ('-v', '--value', {'help': 'Value to set key to'}, {}),
    ('--file', {'help': 'Use contents of file to set key to'}, {}),
    ('--filepart', {'help': 'Use contents of part of the file to set key to'},      {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})
    ]

def doit(args):

    font = args.ifont
    logger = args.logger
    plist = args.plist
    if plist is None:
        plist = "fontinfo"
    if plist not in ("lib", "fontinfo"):
        logger.log("--plist must be either fontinfo or lib", "S")
    elif plist not in font.__dict__:
        font.addfile(plist)
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
        contents = join_lines(fh.readlines())
        set_key_value(font_plist, args.key, contents)
        fh.close()

    # Use some of the file contents to set the key
    if args.key and args.filepart:
        fh = codecs.open(args.filepart, 'r', 'utf-8')
        first_line = fh.readlines()[0]
        contents = first_line.strip()
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


def join_lines(lines):
    """Join lines into a single string.

    Paragraphs should not have newlines in the middle of them.
    To do this for OFL.txt (which is the file generally used with this script),
    various special cases (involving & and ---) needed to be handled.
    """

    preprocessed_lines = []
    for line in lines:
        possible_heading = line.strip()
        possible_heading = possible_heading.replace(' ', '')
        possible_heading = possible_heading.replace('&', '')
        is_heading = all(char.isupper() for char in possible_heading) or possible_heading.startswith('-')
        if line == '\n':
            # Blank lines are kept as they are
            preprocessed_lines.append(line)
        elif is_heading:
            # Text with no lowercase letters is a heading
            preprocessed_lines.append(line.strip() + '\u2028')
        else:
            preprocessed_lines.append(line)

    # Create a single string from the lines
    text = ''.join(preprocessed_lines).strip()

    # Three newline characters are used to separate sections
    text = text.replace('\n\n\n', '\u2028\u2029')

    # A blank line after a heading is a slightly different section
    text = text.replace('\u2028\n', '\u2028\u2028')

    # Two newline characters are used to separate paragraphs
    text = text.replace('\n\n', '\u2029')

    # Remove newlines in the middle of paragraphs
    text = text.replace('\n', ' ')

    # No trailing spaces at the end of paragraphs
    text = text.replace(' ---', '\n---')
    text = text.replace(' \u2029', '\u2029')

    # Use newlines in the final text
    text = text.replace('\u2028', '\n')
    text = text.replace('\u2029', '\n\n')

    return text


# Which fontInfo keys are bit number arrays, max field length for each
bitfieldlength = {
    'openTypeHeadFlags': 16,
    'openTypeOS2Selection': 16,
    'openTypeOS2UnicodeRanges': 64,
    'openTypeOS2CodePageRanges': 32,
    'openTypeOS2Type': 16
}

def set_key_value(font_plist, key, value):
    """Set key to value in font."""

    # Currently setval() only works for integer, real or string.
    # For other items you need to construct an elementtree element and use setelem()

    if key in bitfieldlength:
        set_bitnumber_key_value(font_plist, key, value)
        return
    elif value == 'true' or value == 'false':
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

def set_bitnumber_key_value(font_plist, key, value):
    """Manage keys whose values are bitnumber arrays
        value can be either:
            - comma-separated list of integers identifying bit numbers
                If an integer is prefixed with '-' it clears rather than sets the bit
            - a string of hexadecimal digits, optionally preceded by 'x'
                Converted to binary and replaces all bit values
                up to the length of that binary number
        In both cases, spaces can be used for readability.
    """
    maxbitnum = bitfieldlength[key]

    # Strip spaces from value
    value = value.replace(' ', '')
    # If result is empty, warn and be done
    if len(value) == 0:
        font_plist.font.logger.log(f'{key} unchanged', 'W')
        return

    # Initialize result_value from current key value, if present; convert to set of integer values
    result_value = set() if key not in font_plist else set([int(x.text) for x in font_plist[key][1].findall('integer')])

    # If value is one or more comma-separated decimal integers, parse as such:
    if re.fullmatch(r'-?\d{1,3}(,-?\d{1,3})*', value):
        for w in value.split(','):
            m = re.match(r'(-?)(\d+)$', w)  # should always match
            bitnumber = int(m.group(2))
            if m.group(1):
                result_value.discard(bitnumber)
            else:
                result_value.add(bitnumber)
    # else if hexadecimal string optionally preceded by 'x'
    elif m := re.match(r'x?([0-9a-fA-F]+)$', value):
        # ignore the 'x' if provided
        s = m.group(1)
        startnum = len(s)*4-1
        for hexdigit in s:
            bits = bin(int(hexdigit, 16))[2:].zfill(4)
            for i in range(0, 4):
                bitnumber = startnum-i
                if bits[i] == '0':
                    result_value.discard(bitnumber)
                else:
                    result_value.add(bitnumber)
            startnum -= 4
    # Otherwise the value cannot be interpreted so raise error
    else:
        font_plist.font.logger.log(f'key {key} value {value} could not be interpreted', 'E')

    # Check and sort bit numbers provided
    if max(result_value) >= maxbitnum:
        font_plist.font.logger.log(f'key {key} bit numbers >= {maxbitnum} will be ignored', 'W')
        result_value = [bitnumber for bitnumber in result_value if bitnumber < maxbitnum]
    result_value = sorted(result_value)

    # Finally replace the array
    a = ET.Element('array')
    for bitnumber in result_value:
        ET.SubElement(a, 'integer').text = str(bitnumber)
    font_plist.setelem(key, a)
    font_plist.font.logger.log(key + " adjusted, new value: " + str(result_value), "I")


def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
