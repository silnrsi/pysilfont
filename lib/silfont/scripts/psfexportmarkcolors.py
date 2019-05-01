#!/usr/bin/env python
from __future__ import unicode_literals
'''Write mapping of glyph name to cell mark color to a csv file
- csv format glyphname,colordef'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute
import datetime

suffix = "_colormap"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output csv file'}, {'type': 'outfile', 'def': suffix+'.csv'}),
    ('-c','--color',{'help': 'Export list of glyphs that match color'},{}),
    ('-n','--names',{'help': 'Export colors as names', 'action': 'store_true', 'default': False},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('--nocomments',{'help': 'No comments in output files', 'action': 'store_true', 'default': False},{})]


# Color name definitions, based on the colors provided by app UIs
# g_ names refers to colors definable using the Glyphs UI
namestocolors = {
    'g_red': '0.85,0.26,0.06,1',
    'g_orange': '0.99,0.62,0.11,1',
    'g_brown': '0.65,0.48,0.2,1',
    'g_yellow': '0.97,1,0,1',
    'g_light_green': '0.67,0.95,0.38,1',
    'g_dark_green': '0.04,0.57,0.04,1',
    'g_light_blue': '0,0.67,0.91,1',
    'g_dark_blue': '0.18,0.16,0.78,1',
    'g_purple': '0.5,0.09,0.79,1',
    'g_pink': '0.98,0.36,0.67,1',
    'g_light_grey': '0.75,0.75,0.75,1',
    'g_dark_grey': '0.25,0.25,0.25,1'
}

colorstonames = {v: k for k, v in namestocolors.items()}

def doit(args) :
    font = args.ifont
    outfile = args.output
    logger = args.logger

    # Add initial comments to outfile
    if not args.nocomments :
        outfile.write("# " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + args.cmdlineargs[0] + "\n")
        outfile.write("# "+" ".join(args.cmdlineargs[1:])+"\n\n")

    if args.color :
        colorfilter = args.color
        if not((args.color[0] == "0") or (args.color[0] == "1")) :
            colorfilter = namestocolors.get(args.color, "Error")
            if colorfilter == "Error" : logger.log("Color name not recognized", "E")

    glyphlist = font.deflayer.keys()

    for glyphn in glyphlist :
        glyph = font.deflayer[glyphn]
        colordefraw = ""
        colordef = ""
        if glyph["lib"] :
            lib = glyph["lib"]
            if "public.markColor" in lib :
                colordefraw = lib["public.markColor"][1].text
                colordef = '"' + colordefraw + '"'
                if args.names : colordef = colorstonames.get(colordefraw, colordef)
            if args.color :
                if colorfilter == colordefraw : outfile.write(glyphn + "\n")
        if not args.color : outfile.write(glyphn + "," + colordef + "\n")
    return

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
