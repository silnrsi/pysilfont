#!/usr/bin/env python3
'FontForge: Check for duplicate USVs in unicode or altuni fields'
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

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
        
def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
