#!/usr/bin/env python3
__doc__ = '''generate composite definitions from csv file'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

import re
from silfont.core import execute
import re

argspec = [
    ('output',{'help': 'Output file containing composite definitions'}, {'type': 'outfile'}),
    ('-i','--input',{'help': 'Glyph info csv file'}, {'type': 'incsv', 'def': 'glyph_data.csv'}),
    ('-f','--fontcode',{'help': 'letter to filter for glyph_data'},{}),
    ('--gname', {'help': 'Column header for glyph name', 'default': 'glyph_name'}, {}),
    ('--base', {'help': 'Column header for name of base', 'default': 'base'}, {}),
    ('--usv', {'help': 'Column header for USV'}, {}),
    ('--anchors', {'help': 'Column header(s) for APs to compose', 'default': 'above,below'}, {}),
    ('-r','--report',{'help': 'Set reporting level for log', 'type':str, 'choices':['X','S','E','P','W','I','V']},{}),
    ('-l','--log',{'help': 'Set log file name'}, {'type': 'outfile', 'def': 'csv2comp.log'}),
    ]

def doit(args):
    logger = args.logger
    if args.report: logger.loglevel = args.report
    # infont = args.ifont
    incsv = args.input
    output = args.output

    def csvWarning(msg, exception = None):
        m = "glyph_data warning: %s at line %d" % (msg, incsv.line_num)
        if exception is not None:
            m += '; ' + exception.message
        logger.log(m, 'W')

    if args.fontcode is not None:
        whichfont = args.fontcode.strip().lower()
        if len(whichfont) != 1:
            logger.log('-f parameter must be a single letter', 'S')
    else:
        whichfont = None

    # Which headers represent APs to use:
    apList = args.anchors.split(',')
    if len(apList) == 0:
        logger.log('--anchors option value "%s" is invalid' % args.anchors, 'S')

    # Get headings from csvfile:
    fl = incsv.firstline
    if fl is None: logger.log("Empty input file", "S")
    # required columns:
    try:
        nameCol = fl.index(args.gname)
        baseCol = fl.index(args.base)
        apCols = [fl.index(ap) for ap in apList]
        if args.usv is not None:
            usvCol =  fl.index(args.usv)
        else:
            usvCol = None
    except ValueError as e:
        logger.log('Missing csv input field: ' + e.message, 'S')
    except Exception as e:
        logger.log('Error reading csv input field: ' + e.message, 'S')

    # Now make strip AP names; pair up with columns so easy to iterate:
    apInfo = list(zip(apCols, [x.strip() for x in apList]))

    # If -f specified, make sure we have the fonts column
    if whichfont is not None:
        if 'fonts' not in fl: logger.log('-f requires "fonts" column in glyph_data', 'S')
        fontsCol = fl.index('fonts')

    # RE that matches names of glyphs we don't care about
    namesToSkipRE = re.compile('^(?:[._].*|null|cr|nonmarkingreturn|tab|glyph_name)$',re.IGNORECASE)

    # keep track of glyph names we've seen to detect duplicates
    namesSeen = set()

    # OK, process all records in glyph_data
    for line in incsv:
        base = line[baseCol].strip()
        if len(base) == 0:
            # No composites specified
            continue

        gname = line[nameCol].strip()
        # things to ignore:
        if namesToSkipRE.match(gname): continue
        if whichfont is not None and line[fontsCol] != '*' and line[fontsCol].lower().find(whichfont) < 0:
            continue

        if len(gname) == 0:
            csvWarning('empty glyph name in glyph_data; ignored')
            continue
        if gname.startswith('#'): continue
        if gname in namesSeen:
            csvWarning('glyph name %s previously seen in glyph_data; ignored' % gname)
            continue
        namesSeen.add(gname)

        # Ok, start building the composite
        composite = '%s = %s' %(gname, base)

        # The first component must *not* reference the base; all others *must*:
        seenfirst = False
        for apCol, apName in apInfo:
            component = line[apCol].strip()
            if len(component):
                if not seenfirst:
                    composite += ' + %s@%s' % (component, apName)
                    seenfirst = True
                else:
                    composite += ' + %s@%s:%s' % (component, base, apName)

        # Add USV if present
        if usvCol is not None:
            usv = line[usvCol].strip()
            if len(usv):
                composite += ' | %s' % usv

        # Output this one
        output.write(composite + '\n')

    output.close()

def cmd() : execute("",doit,argspec)
if __name__ == "__main__": cmd()

