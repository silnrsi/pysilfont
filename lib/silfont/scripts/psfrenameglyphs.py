#!/usr/bin/env python
__doc__ = '''Assign new working names to glyphs based on csv input file
- csv format oldname,newname'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.core import execute
from xml.etree import ElementTree as ET
import re
import os
from glob import glob

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-c', '--classfile', {'help': 'Classes file'}, {}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': 'namemap.csv'}),
    ('--mergecomps',{'help': 'turn on component merge', 'action': 'store_true', 'default': False},{}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_renameglyphs.log'})]

csvmap={}

def doit(args) :
    global csvmap

    font = args.ifont
    incsv = args.input
    logger = args.logger
    mergemode = args.mergecomps

    # List of secondary layers (ie layers other than the default)
    secondarylayers = [x for x in font.layers if x.layername != "public.default"]

    # remember all requested mappings:
    masterMap = {}

    # remember all identity mappings
    identityMap = set()

    # remember all glyphs actually renamed:
    nameMap = {}

    # Obtain lib.plist glyph order(s) and psnames if they exist:
    publicGlyphOrder = csGlyphOrder = psnames = displayStrings = None
    if hasattr(font, 'lib'):
        if 'public.glyphOrder' in font.lib:
            publicGlyphOrder = font.lib.getval('public.glyphOrder')     # This is an array
        if 'com.schriftgestaltung.glyphOrder' in font.lib:
            csGlyphOrder = font.lib.getval('com.schriftgestaltung.glyphOrder') # This is an array
        if 'public.postscriptNames' in font.lib:
            psnames = font.lib.getval('public.postscriptNames')   # This is a dict keyed by glyphnames
        if 'com.schriftgestaltung.customParameter.GSFont.DisplayStrings' in font.lib:
            displayStrings = font.lib.getval('com.schriftgestaltung.customParameter.GSFont.DisplayStrings')
    else:
        logger.log("no lib.plist found in font", "W")

    # Renaming within the UFO is done in two passes to make sure we can handle circular renames such as:
    #    someglyph.alt = someglyph
    #    someglyph = someglyph.alt

    # Note that the font, public.glyphOrder and GlyphsApp glyphOrder are all
    # done independently since the same glyph names are not necessarily in all
    # three structures.

    # First pass: process all records of csv, and for each glyph that is to be renamed:
    #   If the new glyphname is not already present, go ahead and rename it now.
    #   If the new glyph name already exists, rename the glyph to a temporary name
    #      and put relevant details in saveforlater[]

    saveforlaterFont = []   # For the font itself
    saveforlaterPGO = []    # For public.GlyphOrder
    saveforlaterCSGO = []   # For GlyphsApp GlyphOrder (com.schriftgestaltung.glyphOrder)
    saveforlaterPSN = []    # For public.postscriptNames
    deletelater = []        # Glyphs we'll delete after merging

    for r in incsv:
        oldname = r[0].strip()
        newname = r[1].strip()
        # ignore header row and rows where the newname is blank or a comment marker
        if oldname == "Name" or oldname.startswith('#') or newname == "":
            continue
        if len(oldname)==0:
            logger.log('empty glyph oldname in glyph_data; ignored', 'W')
            continue
        csvmap[oldname]=newname

        if  oldname == newname:
            # Remember names that don't need to change
            identityMap.add(newname)
        else:
            # Remember all names that need to change
            masterMap[oldname] = newname

        # Handle font first:
        if oldname not in font.deflayer:
            logger.log("glyph name not in font: " + oldname , "I")
        elif newname not in font.deflayer:
            for layer in secondarylayers:
                if newname in layer:
                    logger.log("Glyph %s is already in non-default layers; can't rename %s" % (newname, oldname), "S")
            # Ok, this case is easy: just rename the glyph in all layers
            for layer in font.layers:
                if oldname in layer: layer[oldname].name = newname
            nameMap[oldname] = newname
            logger.log("Pass 1 (Font): Renamed %s to %s" % (oldname, newname), "I")
        elif mergemode:
            mergeglyphs(font.deflayer[oldname], font.deflayer[newname])
            for layer in secondarylayers:
                if oldname in layer:
                    if newname in layer:
                        mergeglyphs(layer[oldname], layer[newname])
                    else:
                        layer[oldname].name = newname

            nameMap[oldname] = newname
            deletelater.append(oldname)
            logger.log("Pass 1 (Font): merged %s to %s" % (oldname, newname), "I")
        else:
            # newname already in font -- but it might get renamed later in which case this isn't actually a problem.
            # For now, then, rename glyph to a temporary name and remember it for second pass
            tempname = gettempname(lambda n : n not in font.deflayer)
            for layer in font.layers:
                if oldname in layer:
                    layer[oldname].name = tempname
            saveforlaterFont.append( (tempname, oldname, newname) )

        # Similar algorithm for public.glyphOrder, if present:
        if publicGlyphOrder:
            if oldname not in publicGlyphOrder:
                logger.log("glyph name not in publicGlyphorder: " + oldname , "I")
            else:
                x = publicGlyphOrder.index(oldname)
                if newname not in publicGlyphOrder:
                    publicGlyphOrder[x] = newname
                    nameMap[oldname] = newname
                    logger.log("Pass 1 (PGO): Renamed %s to %s" % (oldname, newname), "I")
                elif mergemode:
                    del publicGlyphOrder[x]
                    nameMap[oldname] = newname
                    logger.log("Pass 1 (PGO): Removed %s (now using %s)" % (oldname, newname), "I")
                else:
                    tempname = gettempname(lambda n : n not in publicGlyphOrder)
                    publicGlyphOrder[x] = tempname
                    saveforlaterPGO.append( (x, oldname, newname) )

        # And for GlyphsApp glyph order, if present:
        if csGlyphOrder:
            if oldname not in csGlyphOrder:
                logger.log("glyph name not in csGlyphorder: " + oldname , "I")
            else:
                x = csGlyphOrder.index(oldname)
                if newname not in csGlyphOrder:
                    csGlyphOrder[x] = newname
                    nameMap[oldname] = newname
                    logger.log("Pass 1 (csGO): Renamed %s to %s" % (oldname, newname), "I")
                elif mergemode:
                    del csGlyphOrder[x]
                    nameMap[oldname] = newname
                    logger.log("Pass 1 (csGO): Removed %s (now using %s)" % (oldname, newname), "I")
                else:
                    tempname = gettempname(lambda n : n not in csGlyphOrder)
                    csGlyphOrder[x] = tempname
                    saveforlaterCSGO.append( (x, oldname, newname) )

        # Finally, psnames
        if psnames:
            if oldname not in psnames:
                logger.log("glyph name not in psnames: " + oldname , "I")
            elif newname not in psnames:
                psnames[newname] = psnames.pop(oldname)
                nameMap[oldname] = newname
                logger.log("Pass 1 (psn): Renamed %s to %s" % (oldname, newname), "I")
            elif mergemode:
                del psnames[oldname]
                nameMap[oldname] = newname
                logger.log("Pass 1 (psn): Removed %s (now using %s)" % (oldname, newname), "I")
            else:
                tempname = gettempname(lambda n: n not in psnames)
                psnames[tempname] = psnames.pop(oldname)
                saveforlaterPSN.append( (tempname, oldname, newname))

    # Second pass: now we can reprocess those things we saved for later:
    #    If the new glyphname is no longer present, we can complete the renaming
    #    Otherwise we've got a fatal error

    for j in saveforlaterFont:
        tempname, oldname, newname = j
        if newname in font.deflayer: # Only need to check deflayer, since (if present) it would have been renamed in all
            # Ok, this really is a problem
            logger.log("Glyph %s already in font; can't rename %s" % (newname, oldname), "S")
        else:
            for layer in font.layers:
                if tempname in layer:
                    layer[tempname].name = newname
            nameMap[oldname] = newname
            logger.log("Pass 2 (Font): Renamed %s to %s" % (oldname, newname), "I")

    for j in saveforlaterPGO:
        x, oldname, newname = j
        if newname in publicGlyphOrder:
            # Ok, this really is a problem
            logger.log("Glyph %s already in public.GlyphOrder; can't rename %s" % (newname, oldname), "S")
        else:
            publicGlyphOrder[x] = newname
            nameMap[oldname] = newname
            logger.log("Pass 2 (PGO): Renamed %s to %s" % (oldname, newname), "I")

    for j in saveforlaterCSGO:
        x, oldname, newname = j
        if newname in csGlyphOrder:
            # Ok, this really is a problem
            logger.log("Glyph %s already in com.schriftgestaltung.glyphOrder; can't rename %s" % (newname, oldname), "S")
        else:
            csGlyphOrder[x] = newname
            nameMap[oldname] = newname
            logger.log("Pass 2 (csGO): Renamed %s to %s" % (oldname, newname), "I")

    for tempname, oldname, newname in saveforlaterPSN:
        if newname in psnames:
            # Ok, this really is a problem
            logger.log("Glyph %s already in public.postscriptNames; can't rename %s" % (newname, oldname), "S")
        else:
            psnames[newname] = psnames.pop(tempname)
            nameMap[oldname] = newname
            logger.log("Pass 2 (psn): Renamed %s to %s" % (oldname, newname), "I")

    # Rebuild font structures from the modified lists we have:

    # Rebuild glyph order elements:
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

    # Rebuild postscriptNames:
    if psnames:
        dict = ET.Element("dict")
        for n in psnames:
            ET.SubElement(dict, "key").text = n
            ET.SubElement(dict, "string").text = psnames[n]
        font.lib.setelem("public.postscriptNames", dict)

    # Iterate over all glyphs, and fix up any components that reference renamed glyphs
    for layer in font.layers:
        for name in layer:
            glyph = layer[name]
            for component in glyph.etree.findall('./outline/component[@base]'):
                oldname = component.get('base')
                if oldname in nameMap:
                    component.set('base', nameMap[oldname])
                    logger.log(f'renamed component base {oldname} to {component.get("base")} in glyph {name} layer {layer.layername}', 'I')
            lib = glyph['lib']
            if lib:
                if 'com.schriftgestaltung.Glyphs.ComponentInfo' in lib:
                    cielem = lib['com.schriftgestaltung.Glyphs.ComponentInfo'][1]
                    for component in cielem:
                        for i in range(0,len(component),2):
                            if component[i].text == 'name':
                                oldname = component[i+1].text
                                if oldname in nameMap:
                                    component[i+1].text = nameMap[oldname]
                                    logger.log(f'renamed component info {oldname} to {nameMap[oldname]} in glyph {name} layer {layer.layername}', 'I')

    # Delete anything we no longer need:
    for name in deletelater:
        for layer in font.layers:
            if name in layer: layer.delGlyph(name)
        logger.log("glyph %s removed" % name, "I")

    logger.log("%d glyphs renamed in UFO" % (len(nameMap)), "P")

    # Update Display Strings

    if displayStrings:
        changed = False
        glyphRE = re.compile(r'/([a-zA-Z0-9_.-]+)') # regex to match / followed by a glyph name
        for i, dispstr in enumerate(displayStrings):            # Passing the glyphSub function to .sub() causes it to
            displayStrings[i] = glyphRE.sub(glyphsub, dispstr)  # every non-overlapping occurrence of pattern
            if displayStrings[i] != dispstr:
                changed = True
        if changed:
            array = ET.Element("array")
            for dispstr in displayStrings:
                ET.SubElement(array, "string").text = dispstr
            font.lib.setelem('com.schriftgestaltung.customParameter.GSFont.DisplayStrings', array)
            logger.log("com.schriftgestaltung.customParameter.GSFont.DisplayStrings updated", "I")

    # If a classfile was provided, change names within it also
    #
    if args.classfile:

        logger.log("Processing classfile {}".format(args.classfile), "P")

        # In order to preserve comments we use our own TreeBuilder
        class MyTreeBuilder(ET.TreeBuilder):
            def comment(self, data):
                self.start(ET.Comment, {})
                self.data(data)
                self.end(ET.Comment)

        # RE to match separators between glyph names (whitespace):
        notGlyphnameRE = re.compile(r'(\s+)')

        # Keep a list of glyphnames that were / were not changed
        changed = set()
        notChanged = set()

        # Process one token (might be whitespace separator, glyph name, or embedded classname starting with @):
        def dochange(gname, logErrors = True):
            if len(gname) == 0 or gname.isspace() or gname in identityMap or gname.startswith('@'):
                # No change
                return gname
            try:
                newgname = masterMap[gname]
                changed.add(gname)
                return newgname
            except KeyError:
                if logErrors: notChanged.add(gname)
                return gname

        doc = ET.parse(args.classfile, parser=ET.XMLParser(target=MyTreeBuilder()))
        for e in doc.iter(None):
            if e.tag in ('class', 'property'):
                if 'exts' in e.attrib:
                    logger.log("{} '{}' has 'exts' attribute which may need editing".format(e.tag.title(), e.get('name')), "W")
                # Rather than just split() the text, we'll use re and thus try to preserve whitespace
                e.text = ''.join([dochange(x) for x in notGlyphnameRE.split(e.text)])
            elif e.tag is ET.Comment:
                # Go ahead and look for glyph names in comment text but don't flag as error
                e.text = ''.join([dochange(x, False) for x in notGlyphnameRE.split(e.text)])
                # and process the tail as this might be valid part of class or property
                e.tail = ''.join([dochange(x) for x in notGlyphnameRE.split(e.tail)])


        if len(changed):
            # Something in classes changed so rewrite it... saving  backup
            (dn,fn) = os.path.split(args.classfile)
            dn = os.path.join(dn, args.paramsobj.sets['main']['backupdir'])
            if not os.path.isdir(dn):
                os.makedirs(dn)
            # Work out backup name based on existing backups
            backupname = os.path.join(dn,fn)
            nums = [int(re.search(r'\.(\d+)~$',n).group(1)) for n in glob(backupname + ".*~")]
            backupname += ".{}~".format(max(nums) + 1 if nums else 1)
            logger.log("Backing up input classfile to {}".format(backupname), "P")
            # Move the original file to backupname
            os.rename(args.classfile, backupname)
            # Write the output file
            doc.write(args.classfile)

            if len(notChanged):
                logger.log("{} glyphs renamed, {} NOT renamedin {}: {}".format(len(changed), len(notChanged), args.classfile, ' '.join(notChanged)), "W")
            else:
                logger.log("All {} glyphs renamed in {}".format(len(changed), args.classfile), "P")

    return font

def mergeglyphs(mergefrom, mergeto): # Merge any "moving" anchors (i.e., those starting with '_') into the glyph we're keeping
    # Assumption: we are merging one or more component references to just one component; deleting the others
    for a in mergefrom['anchor']:
        aname = a.element.get('name')
        if aname.startswith('_'):
            # We want to copy this anchor to the glyph being kept:
            for i, a2 in enumerate(mergeto['anchor']):
                if a2.element.get('name') == aname:
                    # Overwrite existing anchor of same name
                    mergeto['anchor'][i] = a
                    break
            else:
                # Append anchor to glyph
                mergeto['anchor'].append(a)

def gettempname(f):
    ''' return a temporary glyph name that, when passed to function f(), returns true'''
    # Initialize function attribute for use as counter
    if not hasattr(gettempname, "counter"): gettempname.counter = 0
    while True:
        name = "tempglyph%d" % gettempname.counter
        gettempname.counter += 1
        if f(name): return name


def glyphsub(m): # Function pased to re.sub() when updating display strings
    global csvmap
    gname = m.group(1)
    if gname in csvmap:
        x = '/' + csvmap[gname]
    else:
        x = m.group(0)
    return '/' + csvmap[gname] if gname in csvmap else m.group(0)

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
