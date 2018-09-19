#!/usr/bin/env python
from __future__ import unicode_literals
'''Export the name and unicode of glyphs that have a defined unicode to a csv file. Does not support double-encoded glyphs.
- csv format glyphname,unicode'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney, based on UFOexportPSname.py'

from silfont.core import execute
import datetime

suffix = "_unicodes"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output csv file'}, {'type': 'outfile', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('--nocomments',{'help': 'No comments in output files', 'action': 'store_true', 'default': False},{})]

def doit(args) :
    font = args.ifont
    outfile = args.output

    # Add initial comments to outfile
    if not args.nocomments :
        outfile.write("# " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + args.cmdlineargs[0] + "\n")
        outfile.write("# "+" ".join(args.cmdlineargs[1:])+"\n\n")

    glyphlist = sorted(font.deflayer.keys())

    for glyphn in glyphlist :
        glyph = font.deflayer[glyphn]
        if len(glyph["unicode"]) == 1 :
            unival = glyph["unicode"][0].hex
            outfile.write(glyphn + "," + unival + "\n")
            
    return

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
