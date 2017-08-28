#!/usr/bin/env python
'''Assign new working names to glyphs based on csv input file
- csv format oldname,newname'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

suffix = "_namesmap"
argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': 'namemap.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'renameglyphs.log'})]

def doit(args) :
    font = args.ifont
    # logger = args.logger
    incsv = args.input

   # Obtain lib.plist glyph order(s) and psnames if they exist:
    if 'public.glyphOrder' in font.lib:
        publicGlyphOrder = font.lib.getval('public.glyphOrder')     # This is an array
    if 'com.schriftgestaltung.glyphOrder' in font.lib:
        csGlyphOrder = font.lib.getval('com.schriftgestaltung.glyphOrder') # This is an array
    if 'public.postscriptNames' in font.lib:
        psnames = font.lib.getval('public.postscriptNames')   # This is a dict keyed by glyphnames

    # Renaming is done in two passes to make sure we can handle circular renames such as:
    #    someglyph.alt = someglyph
    #    someglyph = someglyph.alt

    # Note that the font, public.glyphOrder and GlyphsApp glyphOrder are all
    # done independently since the same glyph names are not necessarily in all
    # three structures.

    # First process all records of csv, and for each glyph that is to be renamed:
    #   If the new glyphname is not already present, go ahead and rename it now.
    #   If the new glyph name already exists, rename the glyph to a temporary name
    #      and put relevant details in saveforlater{}

    def gettempname(f):
        ''' return a temporary glyph name that, when passed to function f(), returns true'''
        # Initialize function attribute for use as counter
        if not hasattr(gettempname, "counter"): gettempname.counter = 0
        while True:
            name = "tempglyph%d" % gettempname.counter
            gettempname.counter += 1
            if f(name): return name

    saveforlaterFont = []   # For the font itself
    saveforlaterPGO = []    # For public.GlyphOrder
    saveforlaterCSGO = []   # For GlyphsApp GlyphOrder (com.schriftgestaltung.glyphOrder)
    saveforlaterPSN = []    # For public.postscriptNames

    for r in incsv:
        oldname = r[0]
        newname = r[1]
        # ignore header row and rows where the newname is blank or same as oldname
        if oldname == "Name" or newname == "" or oldname == newname:
            continue

        # Handle font first:
        if oldname not in font.deflayer:
            font.logger.log("glyph name not in font: " + oldname , "I")
        elif newname not in font.deflayer:
            # Ok, this case is easy: just rename the glyph
            font.deflayer[oldname].name = newname
            font.logger.log("Pass 1: Renamed %s to %s" % (oldname, newname), "I")
        else:
            # newname already in font -- but it might get renamed later in which case this isn't actually a problem.
            # For now, then, rename glyph to a temporary name and remember it for second pass
            tempname = gettempname(lambda n : n not in font.deflayer)
            font.deflayer[oldname].name = tempname
            saveforlaterFont.append( (tempname, oldname, newname) )

        # Similar algorithm for public.glyphOrder
        if publicGlyphOrder and oldname in publicGlyphOrder:
            x = publicGlyphOrder.index(oldname)
            if newname not in publicGlyphOrder:
                publicGlyphOrder[x] = newname
            else:
                tempname = gettempname(lambda n : n not in publicGlyphOrder)
                publicGlyphOrder[x] = tempname
                saveforlaterPGO.append( (x, oldname, newname) )

        # And for GlyphsApp glyph order:
        if csGlyphOrder and oldname in csGlyphOrder:
            x = csGlyphOrder.index(oldname)
            if newname not in csGlyphOrder:
                csGlyphOrder[x] = newname
            else:
                tempname = gettempname(lambda n : n not in csGlyphOrder)
                csGlyphOrder[x] = tempname
                saveforlaterCSGO.append( (x, oldname, newname) )

        # Finally, psnames
        if psnames and oldname in psnames:
            if newname not in psnames:
                psnames[newname] = psnames.pop(oldname)
            else:
                tempname = gettempname(lambda n: n not in psnames)
                psnames[tempname] = psnames.pop(oldname)
                saveforlaterPSN.append( (tempname, oldname, newname))

    # Ok, now we can reprocess those things we saved for later:
    for j in saveforlaterFont:
        tempname, oldname, newname = j
        if newname in font.deflayer:
            # Ok, this really is a problem
            font.logger.log("Glyph %s already in font; can't rename %s" % (newname, oldname), "E")
        else:
            font.deflayer[tempname].name = newname
            font.logger.log("Pass 2: Renamed %s to %s" % (oldname, newname), "I")

    for j in saveforlaterPGO:
        x, oldname, newname = j
        if newname in publicGlyphOrder:
            # Ok, this really is a problem
            font.logger.log("Glyph %s already in public.GlyphOrder; can't rename %s" % (newname, oldname), "S")
        else:
            publicGlyphOrder[x] = newname

    for j in saveforlaterCSGO:
        x, oldname, newname = j
        if newname in csGlyphOrder:
            # Ok, this really is a problem
            font.logger.log("Glyph %s already in com.schriftgestaltung.glyphOrder; can't rename %s" % (newname, oldname), "S")
        else:
            csGlyphOrder[x] = newname

    for x, oldname, newname in saveforlaterPSN:
        if newname in psnames:
            # Ok, this really is a problem
            font.logger.log("Glyph %s already in public.postscriptNames; can't rename %s" % (newname, oldname), "S")
        else:
            psnames[newname] = psnames.pop(tempname)


    # Rebuild glyph order elements from the modified lists we have
    if publicGlyphOrder:
        array = ET.Element("array")
        for name in publicGlyphOrder:
            ET.SubElement(array, "string").text = name
        font.lib.setelem("public.glyphOrder", array)

    if csGlyphOrder:
        array = ET.Element("array")
        for name in csGlyphOrder:
            ET.SubElement(array, "string").text = name
        font.lib.setelem("com.schriftgestaltung.glyphOrder", array)

    # Rebuild postscriptNames
    if psnames:
        dict = ET.Element("dict")
        for n in psnames:
            ET.SubElement(dict, "key").text = n
            ET.SubElement(dict, "string").text = psnames[n]
        font.lib.setelem("public.postscriptNames", dict)

    return font

def cmd() : execute("UFO",doit,argspec) 

if __name__ == "__main__": cmd()
