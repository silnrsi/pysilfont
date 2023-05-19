#!/usr/bin/env python3
__doc__ = '''Write mapping of glyph name to postscript name to a csv file
- csv format glyphname,postscriptname'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import datetime

suffix = "_psnamesmap"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Ouput csv file'}, {'type': 'outfile', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('--nocomments',{'help': 'No comments in output files', 'action': 'store_true', 'default': False},{})]

def doit(args) :
    font = args.ifont
    outfile = args.output

    # Add initial comments to outfile
    if not args.nocomments :
        outfile.write("# " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + args.cmdlineargs[0] + "\n")
        outfile.write("# "+" ".join(args.cmdlineargs[1:])+"\n\n")

    glyphlist = font.deflayer.keys()
    missingnames = False

    for glyphn in glyphlist :
        glyph = font.deflayer[glyphn]
        # Find PSname if present
        PSname = None
        if "lib" in glyph :
            lib = glyph["lib"]
            if "public.postscriptname" in lib : PSname = lib["public.postscriptname"][1].text
        if PSname:
            outfile.write(glyphn + "," + PSname + "\n")
        else :
            font.logger("No psname for " + glyphn, "W")
            missingnames = True
    if missingnames : font.logger("Some glyphs had no psnames - see log file","E")
    return

def cmd() : execute("UFO",doit,argspec) 
if __name__ == "__main__": cmd()
