#!/usr/bin/env python
'Set Glyph colours based on a csv file - format glyphname,colour'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont', 'def': 'new'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'infile', 'def': 'colourGlyphs.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'colourGlyphs.log'})]

def doit(args) :
    font=args.ifont
    inpf = args.input
    logf = args.log
# define colours
    colours = {
        'black'  :0x000000,
        'red'    :0xFF0000,
        'green'  :0x00FF00,
        'blue'   :0x0000FF,
        'cyan'   :0x00FFFF,
        'magenta':0xFF00FF,
        'yellow' :0xFFFF00,
        'white'  :0xFFFFFF }

# Change colour of Glyphs
    for line in inpf.readlines() :
        glyphn, colour = line.strip().split(",")  # will exception if not 2 elements
        colour=colour.lower()
        if glyphn[0] in '"\'' : glyphn = glyphn[1:-1]  # slice off quote marks, if present
        if glyphn not in font:
            logf.write("Glyph %s not in font\n" % (glyphn))
            print "Glyph %s not in font" % (glyphn)
            continue
        g = font[glyphn]
        if colour in colours.keys():
            g.color=colours[colour]
        else:
            logf.write("Glyph: %s - non-standard colour %s\n" % (glyphn,colour))
            print "Glyph: %s - non-standard colour %s" % (glyphn,colour)

    logf.close()
    return font

def cmd() : execute("FF",doit,argspec) 
if __name__ == "__main__": cmd()
