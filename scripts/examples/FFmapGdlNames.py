#!/usr/bin/env python
'''Write mapping of graphite names to new graphite names based on:
   - an original ttf font
   - the gdl file produced by makeGdl when original font was produced
   - a csv mapping glyph names used in original ttf to those in the new font '''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.gdl.psnames as ps
import datetime

suffix = "_mapGDLnames"
argspec = [
    ('ifont',{'help': 'Input ttf font file'}, {'type': 'infont'}),
    ('-g','--gdl',{'help': 'Input gdl file'}, {'type': 'infile', 'def': '.gdl'}),
    ('-m','--mapping',{'help': 'Mapping csv file'}, {'type': 'incsv', 'def': '_map.csv'}),
    ('-o','--output',{'help': 'Ouput csv file'}, {'type': 'outfile', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('--nocomments',{'help': 'No comments in output files', 'action': 'store_true', 'default': False},{})]

def doit(args) :
    logger = args.paramsobj.logger
    # Check input font is a ttf
    fontfile = args.cmdlineargs[1]
    if fontfile[-3:] <> "ttf" :
        logger.log("Input font needs to be a ttf file", "S")

    font = args.ifont
    gdlfile = args.gdl
    mapping = args.mapping
    outfile = args.output

    # Add initial comments to outfile
    if not args.nocomments :
        outfile.write("# " + datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S ") + args.cmdlineargs[0] + "\n")
        outfile.write("# "+" ".join(args.cmdlineargs[1:])+"\n\n")

    # Process gdl file
    oldgrnames = {}
    for line in args.gdl :
        # Look for lines of format <grname> = glyphid(nnn)...
        pos = line.find(" = glyphid(")
        if pos == -1 : continue
        grname = line[0:pos]
        gid = line[pos+11:line.find(")")]
        oldgrnames[int(gid)]=grname

    # Create map from AGL name to new graphite name
    newgrnames = {}
    mapping.numfields = 2
    for line in mapping :
        AGLname = line[1]
        SILname = line[0]
        grname = ps.Name(SILname).GDL()
        newgrnames[AGLname] = grname

    # Find glyph names in ttf font
    for glyph in font.glyphs():
        gid = glyph.originalgid
        gname = glyph.glyphname
        oldgrname = oldgrnames[gid] if gid in oldgrnames else None
        newgrname = newgrnames[gname] if gname in newgrnames else None
        outfile.write(oldgrname + "," + newgrname+"\n")

    outfile.close()
    return

execute("FF",doit, argspec)
