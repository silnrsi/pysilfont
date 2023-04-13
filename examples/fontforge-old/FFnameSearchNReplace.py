#!/usr/bin/env python3
'Search and replace strings in Glyph names. Strings can be regular expressions'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import re

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('search',{'help': 'Expression to search for'}, {}),
    ('replace',{'help': 'Expression to replace with'}, {}),    
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'searchNReplace.log'})]

def doit(args) :
    font=args.ifont
    search=args.search
    replace=args.replace
    logf = args.log
    
    changes=False
    for glyph in font :
        newname = re.sub(search, replace, glyph)
        if newname != glyph :
            font[glyph].glyphname=newname
            changes=True
            logf.write('Glyph %s renamed to %s\n' % (glyph,newname))
    logf.close()
    if changes :
        return font
    else :
        return

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
