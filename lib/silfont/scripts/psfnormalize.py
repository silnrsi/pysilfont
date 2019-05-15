#!/usr/bin/env python
from __future__ import unicode_literals
__doc__ = '''Normalize a UFO and optionally convert between UFO2 and UFO3'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_normalize.log'}),
    ('-v','--version',{'help': 'UFO version to convert to (2, 3 or 3ff)'},{})]

def doit(args) :

    if args.version is not None :
        v = args.version.lower()
        if v in ("2","3","3ff") :
            if v == "3ff": # Special action for testing with FontForge import
                v = "3"
                args.ifont.outparams['format1Glifs'] = True
            args.ifont.outparams['UFOversion'] = v
        else:
            args.logger.log("-v, --version must be one of 2,3 or 3ff", "S")

    return args.ifont

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
