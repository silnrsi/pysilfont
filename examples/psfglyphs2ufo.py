#!/usr/bin/env python
'''Export fonts in a GlyphsApp file to UFOs'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute

import glyphsLib

argspec = [
    ('glyphsfont',{'help': 'Input font file'}, {'type': 'filename'}),
    ('masterdir',{'help': 'Output directory for masters'}, {}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_glyphs2ufo.log'})]

def doit(args) :
    master_dir = args.masterdir
    ufomasters = glyphsLib.build_masters(args.glyphsfont, master_dir)

def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
