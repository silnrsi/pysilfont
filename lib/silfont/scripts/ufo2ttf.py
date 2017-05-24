#!/usr/bin/env python
'Convert a UFO into a ttf file without OpenType tables'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Alan Ward'

# Compared to fontmake it does not decompose glyphs or remove overlaps 
# and curve conversion seems to happen in a different way.

# The easiest way to install all the needed libraries is to install fontmake.
#   [sudo] pip install fontmake
# If you want to isolate all the libraries fontmake needs,
# you can install fontmake in a virtual environment and run this script there

# TODO: rename according to pysilfont conventions
# TODO: use pysilfont framework
# TODO: improve command line parsing

import sys
import defcon, ufo2ft.outlineCompiler

try:
    ufo_fn = sys.argv[1]
    ttf_fn = sys.argv[2]
except:
    print("ufo2ttf <ufo> <output ttf>")
    sys.exit()

PUBLIC_PREFIX = 'public.'

ufo = defcon.Font(ufo_fn)

# print('Converting UFO to ttf and compiling fea')
# font = ufo2ft.compileTTF(ufo,
#     glyphOrder = ufo.lib.get(PUBLIC_PREFIX + 'glyphOrder'),
#     useProductionNames = False)

print('Converting UFO to ttf without OT')
outlineCompiler = ufo2ft.outlineCompiler.OutlineTTFCompiler(ufo,
    glyphOrder=ufo.lib.get(PUBLIC_PREFIX + 'glyphOrder'),
    convertCubics=True)
font = outlineCompiler.compile()

print('Saving ttf file')
font.save(ttf_fn)

print('Done')
