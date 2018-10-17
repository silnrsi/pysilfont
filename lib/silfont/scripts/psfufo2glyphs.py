#!/usr/bin/env python
from __future__ import unicode_literals
'''Reads a designSpace file and create a Glyphs file from its linked ufos'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

from glyphsLib import to_glyphs
from fontTools.designspaceLib import DesignSpaceDocument

argspec = [
    ('designspace', {'help': 'Input designSpace file'}, {'type': 'filename'}),
    ('glyphsfile', {'help': 'Output glyphs file name', 'nargs': '?' }, {'type': 'filename', 'def': 'temp.glyphs'}),
    ('--nofixes', {'help': 'Bypass code fixing data', 'action': 'store_true', 'default': False}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_ufo2glyphs.log'})]

# This is just bare-bones code at present!

def doit(args):
    logger = args.logger
    logger.log("Opening designSpace file", "I")
    ds = DesignSpaceDocument()
    ds.read(args.designspace)
    glyphsfont = to_glyphs(ds)
    logger.log("Writing glyphs file", "I")
    glyphsfont.save(args.glyphsfile)

def cmd(): execute(None, doit, argspec)
if __name__ == "__main__": cmd()
