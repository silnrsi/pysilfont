#!/usr/bin/env python
'UFO handling script under development'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.UFOlibtest import *

font = Ufont(ufodir=sys.argv[1])


#font.outparams["UFOversion"] = "3"
#font.outparams["plistIndentFirst"] = "  "
#font.outparams["indentFirst"] = "\t"
#font.outparams["indentIncr"] = "\t"
#font.outparams["indentML"] = True

testn = "barx"
if testn in font.layers[0] :
    glif = font.layers[0][testn]
    for i in glif :
        print "-------------------"
        print i
        print glif[i]
        index = glif[i]['index']
        print glif.etree[index]
    glif.outparams = font.outparams.copy()
    glif.outparams["indentFirst"] = "  "
    glif.outparams["indentIncr"] = "  "



print "<<<< Writing font out >>>>"
#print font.outparams
font.write("out.ufo")
    
sys.exit()
