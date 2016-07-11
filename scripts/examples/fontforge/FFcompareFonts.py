#!/usr/bin/env python
'Compare two fonts based on specified criteria and report differences'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.genlib import execute

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ifont2',{'help': 'Input font file 2'}, {'type': 'infont', 'def': 'new'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'compareFonts.log'}),
    ('-o','--options',{'help': 'Options', 'choices': ['c'], 'nargs': '*'}, {})
    ]

def doit(args) :
    font1=args.ifont
    font2=args.ifont2
    logf = args.log
    options = args.options
    logf.write("Comparing fonts: \n %s (%s)\n %s (%s)\n" % (font1.path,font1.fontname,font2.path,font2.fontname))
    if options <> None : logf.write('with options: %s\n' % (options))
    logf.write("\n")
    compare(font1,font2,logf,options)
    compare(font2,font1,logf,None) # Compare again the other way around, just looking for missing Glyphs
    logf.close()
    return

def compare(fonta,fontb,logf,options) :
    for glyph in fonta :
        if glyph in fontb :
            if options <> None : # Do extra checks based on options supplied
                ga=fonta[glyph]
                gb=fontb[glyph]
                for opt in options :
                    if opt == "c" :
                        if len(ga.references) <> len(gb.references) :
                            logf.write("Glyph %s: number of components is different - %s v %s\n" % (glyph,len(ga.references),len(gb.references)))
        else :
            logf.write("Glyph %s missing from %s\n" % (glyph,fonta.path))

execute("FF",doit, argspec)
