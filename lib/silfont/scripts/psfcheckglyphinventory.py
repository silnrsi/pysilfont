#!/usr/bin/env python
__doc__ = '''Warn for differences in glyph inventory and encoding between UFO and input file (e.g., glyph_data.csv). 
Input file can be: 
    - simple text file with one glyph name per line
    - csv file with headers, using headers "glyph_name" and, if present, "USV"'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.core import execute

argspec = [
    ('ifont', {'help': 'Input UFO'}, {'type': 'infont'}),
    ('-i', '--input', {'help': 'Input text file, default glyph_data.csv in current directory', 'default': 'glyph_data.csv'}, {'type': 'incsv'}),
    ('--indent', {'help': 'size of indent (default 10)', 'type': int, 'default': 10}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_checkinventory.log'})]

def doit(args):
    font = args.ifont
    incsv = args.input
    logger = args.logger
    indent = ' '*args.indent

    if not (args.quiet or 'scrlevel' in args.paramsobj.sets['command line']):
        logger.raisescrlevel('W')  # Raise level to W if not already W or higher

    def csvWarning(msg, exception=None):
        m = f'glyph_data line {incsv.line_num}: {msg}'
        if exception is not None:
            m += '; ' + exception.message
        logger.log(m, 'W')

    # Get glyph names and encoding from input file
    glyphFromCSVuid = {}
    uidFromCSVglyph = {}

    # Identify file format (plain text or csv) from first line
    # If csv file, it must have headers for "glyph_name" and "USV"
    fl = incsv.firstline
    if fl is None: logger.log('Empty input file', 'S')
    numfields = len(fl)
    incsv.numfields = numfields
    usvCol = None  # Use this as a flag later to determine whether to check USV inventory
    if numfields > 1:  # More than 1 column, so must have headers
        # Required columns:
        try:
            nameCol = fl.index('glyph_name');
        except ValueError as e:
            logger.log('Missing csv input field: ' + e.message, 'S')
        except Exception as e:
            logger.log('Error reading csv input field: ' + e.message, 'S')
        # Optional columns:
        usvCol = fl.index('USV') if 'USV' in fl else None

        next(incsv.reader, None)  # Skip first line with headers in

        glyphList = set()
        for line in incsv:
            gname = line[nameCol]
            if len(gname) == 0 or line[0].strip().startswith('#'):
                continue    # No need to include cases where name is blank or comment
            glyphList.add(gname)

            # Process USV
            # could be empty string, a single USV or space-separated list of USVs
            try:
                uidList = [int(x, 16) for x in line[usvCol].split()]
            except Exception as e:
                csvWarning("invalid USV '%s' (%s); ignored: " % (line[usvCol], e.message))
                uidList = []
            if len(uidList) == 1:
                # Handle simple encoded glyphs
                uid = uidList[0]
                if uid in glyphFromCSVuid:
                    csvWarning('USV %04X previously seen; ignored' % uid)
                    uidList = []
                else:
                    # Remember this glyph
                    glyphFromCSVuid[uid] = gname
                    uidFromCSVglyph[gname] = uid
    elif numfields == 1:   # Simple text file.
        glyphList = set(line[0] for line in incsv)
    else:
        logger.log('Invalid csv file', 'S')

    # Get the list of glyphs in the UFO
    ufoList = set(font.deflayer.keys())

    notInUFO = glyphList - ufoList
    notInGlyphData = ufoList - glyphList

    if len(notInUFO):
        logger.log('Glyphs present in glyph_data but missing from UFO:\n' + '\n'.join(indent + g for g in sorted(notInUFO)), 'W')

    if len(notInGlyphData):
        logger.log('Glyphs present in UFO but missing from glyph_data:\n' + '\n'.join(indent + g for g in sorted(notInGlyphData)), 'W')

    if len(notInUFO) == 0 and len(notInGlyphData) == 0:
        logger.log('No glyph inventory differences found', 'P')

    if usvCol:
        # We cam check USV inventory of glyphs in common
        inBoth = glyphList & ufoList   # Glyphs we want to examine
        csvEncodings = set(f'{gname}|{uidFromCSVglyph[gname]:04X}' for gname in filter(lambda x: x in uidFromCSVglyph, inBoth))
        ufoEncodings = set(f'{gname}|{int(x.hex, 16):04X}' for gname in inBoth for x in font.deflayer[gname]['unicode'])

        notInUFO = csvEncodings - ufoEncodings
        notInGlyphData = ufoEncodings - csvEncodings

        if len(notInUFO):
            logger.log('Encodings present in glyph_data but missing from UFO:\n' + '\n'.join(indent + g for g in sorted(notInUFO)), 'W')

        if len(notInGlyphData):
            logger.log('Encodings present in UFO but missing from glyph_data:\n' + '\n'.join(indent + g for g in sorted(notInGlyphData)), 'W')

        if len(notInUFO) == 0 and len(notInGlyphData) == 0:
            logger.log('No glyph encoding differences found', 'P')

    else:
        logger.log('Glyph encodings not compared', 'P')


def cmd(): execute('UFO', doit, argspec)
if __name__ == '__main__': cmd()
