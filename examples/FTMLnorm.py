#!/usr/bin/env python3
'Normalize an FTML file'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.ftml as ftml
from xml.etree import cElementTree as ET

argspec = [
    ('infile',{'help': 'Input ftml file'}, {'type': 'infile'}),
    ('outfile',{'help': 'Output ftml file', 'nargs': '?'}, {'type': 'outfile', 'def': '_new.xml'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_ftmltest.log'})
    ]

def doit(args) :
    f = ftml.Fxml(args.infile)
    f.save(args.outfile)

def cmd() : execute("",doit,argspec) 
if __name__ == "__main__": cmd()execute("", doit, argspec)

