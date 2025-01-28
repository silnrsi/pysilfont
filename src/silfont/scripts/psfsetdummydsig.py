#!/usr/bin/env python3

__doc__ = 'Put a dummy DSIG table into a ttf font'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Nicolas Spalinger'

from silfont.core import execute
from fontTools import ttLib

argspec = [
    ('-i', '--ifont', {'help': 'Input ttf font file'}, {}),
    ('-o', '--ofont', {'help': 'Output font file'}, {}),
    ('-l', '--log', {'help': 'Optional log file'}, {'type': 'outfile', 'def': 'dummydsig.log', 'optlog': True})]


def doit(args):

    ttf = ttLib.TTFont(args.ifont)

    newDSIG = ttLib.newTable("DSIG")
    newDSIG.ulVersion = 1
    newDSIG.usFlag = 0
    newDSIG.usNumSigs = 0
    newDSIG.signatureRecords = []
    ttf.tables["DSIG"] = newDSIG

    args.logger.log('Saving the output ttf file with dummy DSIG table', 'P')
    ttf.save(args.ofont)

    args.logger.log('Done', 'P')


def cmd(): execute("FT", doit, argspec)
if __name__ == '__main__': cmd()
