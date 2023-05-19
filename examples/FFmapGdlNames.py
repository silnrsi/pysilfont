#!/usr/bin/env python3
'''Write mapping of graphite names to new graphite names based on:
   - two ttf files
   - the gdl files produced by makeGdl run against those fonts
        This could be different versions of makeGdl
   - a csv mapping glyph names used in original ttf to those in the new font '''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import datetime

suffix = "_mapGDLnames2"
argspec = [
    ('ifont1',{'help': 'First ttf font file'}, {'type': 'infont'}),
    ('ifont2',{'help': 'Second ttf font file'}, {'type': 'infont'}),
    ('gdl1',{'help': 'Original make_gdl file'}, {'type': 'infile'}),
    ('gdl2',{'help': 'Updated make_gdl file'}, {'type': 'infile'}),
    ('-m','--mapping',{'help': 'Mapping csv file'}, {'type': 'incsv', 'def': '_map.csv'}),
    ('-o','--output',{'help': 'Ouput csv file'}, {'type': 'outfile', 'def': suffix+'.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'.log'}),
    ('--nocomments',{'help': 'No comments in output files', 'action': 'store_true', 'default': False},{})]

def doit(args) :
    logger = args.paramsobj.logger
    # Check input fonts are ttf
    fontfile1 = args.cmdlineargs[1]
    fontfile2 = args.cmdlineargs[2]

    if fontfile1[-3:] != "ttf" or fontfile2[-3:] != "ttf" :
        logger.log("Input fonts needs to be ttf files", "S")

    font1 = args.ifont1
    font2 = args.ifont2
    gdlfile1 = args.gdl1
    gdlfile2 = args.gdl2
    mapping = args.mapping
    outfile = args.output

    # Add initial comments to outfile
    if not args.nocomments :
        outfile.write("# " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + args.cmdlineargs[0] + "\n")
        outfile.write("# "+" ".join(args.cmdlineargs[1:])+"\n\n")

    # Process gdl files
    oldgrnames = {}
    for line in gdlfile1 :
        # Look for lines of format <grname> = glyphid(nnn)...
        pos = line.find(" = glyphid(")
        if pos == -1 : continue
        grname = line[0:pos]
        gid = line[pos+11:line.find(")")]
        oldgrnames[int(gid)]=grname

    newgrnames = {}
    for line in gdlfile2 :
        # Look for lines of format <grname> = glyphid(nnn)...
        pos = line.find(" = glyphid(")
        if pos == -1 : continue
        grname = line[0:pos]
        gid = line[pos+11:line.find(")")]
        newgrnames[int(gid)]=grname

    # Process mapping file
    SILnames = {}
    mapping.numfields = 2
    for line in mapping : SILnames[line[1]] = line[0]

    # Map SIL name to gids in font 2
    SILtogid2={}
    for glyph in font2.glyphs(): SILtogid2[glyph.glyphname] = glyph.originalgid

    # Combine all the mappings via ttf1!
    cnt1 = 0
    cnt2 = 0
    for glyph in font1.glyphs():
        gid1 = glyph.originalgid
        gname1 = glyph.glyphname
        gname2 = SILnames[gname1]
        gid2 = SILtogid2[gname2]
        oldgrname = oldgrnames[gid1] if gid1 in oldgrnames else None
        newgrname = newgrnames[gid2] if gid2 in newgrnames else None
        if oldgrname is None or newgrname is None :
            print type(gid1), gname1, oldgrname
            print gid2, gname2, newgrname
            cnt2 += 1
            if cnt2 > 10 : break
        else:
            outfile.write(oldgrname + "," + newgrname+"\n")
            cnt1 += 1

    print cnt1,cnt2

    outfile.close()
    return

execute("FF",doit, argspec)
