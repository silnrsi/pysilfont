#!/usr/bin/env python
'FontForge: Check for duplicate USVs in unicode or altuni fields'
__url__ = 'http://projects.palaso.org/projects/pysilfont'
__copyright__ = 'Copyright (c) 2013, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from silfont.fontforge.framework import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-o','--output',{'help': 'Output text file'}, {'type': 'outfile', 'def': 'DupUSV.txt'})]

def doit(args) :
    font = args.ifont
    outf = args.output

    # Process unicode and altunicode for all glyphs
    usvs={}
    for glyph in font:
        g = font[glyph]
        if g.unicode != -1:
            usv=UniStr(g.unicode)
            AddUSV(usvs,usv,glyph)
        # Check any alternate usvs
        altuni=g.altuni
        if altuni != None:
            for au in altuni:
                usv=UniStr(au[0]) # (may need to check variant flag)
                AddUSV(usvs,usv,glyph + ' (alt)')
                
    items = usvs.items()
    items = filter(lambda x: len(x[1]) > 1, items)
    items.sort()

    for i in items:
        usv = i[0]
        print usv + ' has duplicates'
        gl = i[1]
        glyphs = gl[0]
        for j in range(1,len(gl)):
            glyphs = glyphs + ', ' + gl[j]

        outf.write('%s: %s\n' % (usv,glyphs))

    outf.close()
    print "Done!"

def UniStr(u):
    if u:
        return "U+{0:04X}".format(u)
    else:
        return "No USV" #length same as above

def AddUSV(usvs,usv,glyph):
    if not usvs.has_key(usv):
        usvs[usv] = [glyph]
    else:
        usvs[usv].append(glyph)
        
execute(doit, argspec)
