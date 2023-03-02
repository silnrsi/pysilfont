#!/usr/bin/env python
__doc__ = '''Deletes glyphs from a UFO based on list. Can instead delete glyphs not in list.'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute
from xml.etree import ElementTree as ET

argspec = [
    ('ifont', {'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont', {'help': 'Output font file', 'nargs': '?'}, {'type': 'outfont'}),
    ('-i', '--input', {'help': 'Input text file, one glyphname per line'}, {'type': 'infile', 'def': 'glyphlist.txt'}),
    ('--reverse',{'help': 'Remove glyphs not in list instead', 'action': 'store_true', 'default': False},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'deletedglyphs.log'})]

def doit(args) :
    font = args.ifont
    listinput = args.input
    logger = args.logger

    glyphlist = []
    for line in listinput.readlines():
        glyphlist.append(line.strip())

    deletelist = []

    if args.reverse:
        for glyphname in font.deflayer:
            if glyphname not in glyphlist:
                deletelist.append(glyphname)
    else:
        for glyphname in font.deflayer:
            if glyphname in glyphlist:
                deletelist.append(glyphname)

    secondarylayers = [x for x in font.layers if x.layername != "public.default"]

    liststocheck = ('public.glyphOrder', 'public.postscriptNames', 'com.schriftgestaltung.glyphOrder')
    liblists = [[],[],[]]; inliblists = [[],[],[]]
    if hasattr(font, 'lib'):
        for (i,listn) in enumerate(liststocheck):
            if listn in font.lib:
                liblists[i] = font.lib.getval(listn)
    else:
        logger.log("No lib.plist found in font", "W")

    # Now loop round deleting the glyphs etc
    logger.log("Deleted glyphs:", "I")

    # With groups and kerning, create dicts representing then plists (to make deletion of members easier) and indexes by glyph/member name
    kgroupprefixes = {"public.kern1.": 1, "public.kern2.": 2}
    gdict = {}
    kdict = {}
    groupsbyglyph = {}
    ksetsbymember = {}

    groups = font.groups if hasattr(font, "groups") else []
    kerning = font.kerning if hasattr(font, "kerning") else []
    if groups:
        for gname in groups:
            group = groups.getval(gname)
            gdict[gname] = group
            for glyph in group:
                if glyph in groupsbyglyph:
                    groupsbyglyph[glyph].append(gname)
                else:
                    groupsbyglyph[glyph] = [gname]
    if kerning:
        for setname in kerning:
            kset = kerning.getval(setname)
            kdict[setname] = kset
            for member in kset:
                if member in ksetsbymember:
                    ksetsbymember[member].append(setname)
                else:
                    ksetsbymember[member] = [setname]

    # Loop round doing the deleting
    for glyphn in sorted(deletelist):
        # Delete from all layers
        font.deflayer.delGlyph(glyphn)
        deletedfrom = "Default layer"
        for layer in secondarylayers:
            if glyphn in layer:
                deletedfrom += ", " + layer.layername
                layer.delGlyph(glyphn)
        # Check to see if the deleted glyph is in any of liststocheck
        stillin = None
        for (i, liblist) in enumerate(liblists):
            if glyphn in liblist:
                inliblists[i].append(glyphn)
                stillin = stillin + ", " + liststocheck[i] if stillin else liststocheck[i]

        logger.log("  " + glyphn + " deleted from: " + deletedfrom, "I")
        if stillin: logger.log("  " + glyphn + " is still in " + stillin, "I")

        # Process groups.plist and kerning.plist

        tocheck = (glyphn, "public.kern1." + glyphn, "public.kern2." + glyphn)
        # First delete whole groups and kern pair sets
        for kerngroup in tocheck[1:]: # Don't check glyphn when deleting groups:
            if kerngroup in gdict: gdict.pop(kerngroup)
        for setn in tocheck:
            if setn in kdict: kdict.pop(setn)
        # Now delete members within groups and kern pair sets
        if glyphn in groupsbyglyph:
            for groupn in groupsbyglyph[glyphn]:
                if groupn in gdict: # Need to check still there, since whole group may have been deleted above
                    group = gdict[groupn]
                    del group[group.index(glyphn)]
        for member in tocheck:
            if member in ksetsbymember:
                for setn in ksetsbymember[member]:
                    if setn in kdict: del kdict[setn][member]
        # Now need to recreate groups.plist and kerning.plist
        if groups:
            for group in list(groups): groups.remove(group)  # Empty existing contents
            for gname in gdict:
                elem = ET.Element("array")
                if gdict[gname]: # Only create if group is not empty
                    for glyph in gdict[gname]:
                        ET.SubElement(elem, "string").text = glyph
                    groups.setelem(gname, elem)
        if kerning:
            for kset in list(kerning): kerning.remove(kset)  # Empty existing contents
            for kset in kdict:
                elem = ET.Element("dict")
                if kdict[kset]:
                    for member in kdict[kset]:
                        ET.SubElement(elem, "key").text = member
                        ET.SubElement(elem, "integer").text = str(kdict[kset][member])
                    kerning.setelem(kset, elem)

    logger.log(str(len(deletelist)) + " glyphs deleted. Set logging to I to see details", "P")
    inalist = set(inliblists[0] + inliblists[1] + inliblists[2])
    if inalist: logger.log(str(len(inalist)) + " of the deleted glyphs are still in some lib.plist entries.", "W")

    return font

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()

