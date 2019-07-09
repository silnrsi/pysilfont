#!/usr/bin/env python
from __future__ import unicode_literals
__doc__ = '''Create a list of glyphs to import from a list of characters.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bobby de Vos'

from silfont.core import execute

suffix = "_psfgetglyphnames"
argspec = [
    ('ifont',{'help': 'Font file to copy from'}, {'type': 'infont'}),
    ('glyphs',{'help': 'List of glyphs for psfcopyglyphs'}, {'type': 'outfile'}),
    ('-i', '--input', {'help': 'List of characters to import'}, {'type': 'infile', 'def': None}),
    ('-a','--aglfn',{'help': 'AGLFN list'}, {'type': 'incsv', 'def': None}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'})
    ]

def doit(args) :

    font = args.ifont

    aglfn = dict()
    if args.aglfn:
        # Load Adobe Glyph List For New Fonts (AGLFN)
        incsv = args.aglfn
        incsv.numfields = 3

        for line in incsv:
            usv = line[0]
            aglfn_name = line[1]

            codepoint = int(usv, 16)
            aglfn[codepoint] = aglfn_name

    # Gather data from the UFO
    cmap = dict()
    for glyph in font:
        for codepoint in glyph.unicodes:
            cmap[codepoint] = glyph.name

    # Determine list of glyphs that need to be copied
    header = ('glyph_name', 'rename', 'usv')
    glyphs = args.glyphs
    row = ','.join(header)
    glyphs.write(row + '\n')

    for line in args.input:

        # Ignore comments
        line = line.partition('#')[0]
        line = line.strip()

        # Ignore blank lines
        if line == '':
            continue

        # Specify the glyph to copy
        codepoint = int(line, 16)
        usv = '{:04X}'.format(codepoint)
        if codepoint in cmap:
            aglfn_name = aglfn.get(codepoint, '')
            glyph_name = cmap[codepoint]
            if '_' in glyph_name and aglfn_name == '':
                aglfn_name = glyph_name.replace('_', '')
            row = ','.join((glyph_name, aglfn_name, usv))
            glyphs.write(row + '\n')


def cmd() : execute("FP",doit, argspec)
if __name__ == "__main__": cmd()
