#!/usr/bin/env python
'UFO handling script under development'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.UFOlibtest import *

font = Ufont(ufodir=sys.argv[1])
outfont = sys.argv[2]

#font.outparams["UFOversion"] = "3"             # Change UFO version; default is original UFO version
#font.outparams["plistIndentFirst"] = "  "      # Default is ""
#font.outparams["indentFirst"] = "\t"           # Default is 2 spaces
#font.outparams["indentIncr"] = "\t"            # Default is 2 spaces
#font.outparams["indentML"] = True              # Default is not to indent extra lines on MultiLine text values, eg license text

print "Writing font out to", outfont
font.write(outfont)