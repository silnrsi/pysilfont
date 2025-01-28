#!/usr/bin/env python3
''' Demo of how to chain calls to multiple scripts together.
Running
   python chaindemo.py infont outfont --featfile feat.csv --uidsfile uids.csv
will run execute() against psfnormalize, psfsetassocfeat and psfsetassocuids passing the font, parameters
and logger objects from one call to the next.  So:
- the font is only opened once and written once
- there is a single log file produced
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, chain
import silfont.scripts.psfnormalize as psfnormalize
import silfont.scripts.psfsetassocfeat as psfsetassocfeat
import silfont.scripts.psfsetassocuids as psfsetassocuids

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('--featfile',{'help': 'Associate features csv'}, {'type': 'filename'}),
    ('--uidsfile', {'help': 'Associate uids csv'}, {'type': 'filename'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_chain.log'})]

def doit(args) :

    argv = ['psfnormalize', 'dummy'] # 'dummy' replaces input font since font object is being passed.  Other parameters could be added.
    font = chain(argv, psfnormalize.doit, psfnormalize.argspec, args.ifont, args.paramsobj, args.logger, args.quiet)

    argv = ['psfsetassocfeat', 'dummy', '-i', args.featfile]
    font = chain(argv, psfsetassocfeat.doit, psfsetassocfeat.argspec, font,       args.paramsobj, args.logger, args.quiet)

    argv = ['psfsetassocuids', 'dummy', '-i', args.uidsfile]
    font = chain(argv, psfsetassocuids.doit, psfsetassocuids.argspec, font,       args.paramsobj, args.logger, args.quiet)

    return font

def cmd() : execute("UFO",doit, argspec)

if __name__ == "__main__": cmd()

