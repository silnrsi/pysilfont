#!/usr/bin/env python
__doc__ = '''Make changes needed to a UFO following processing by FontLab 7.
Various items are reset using the backup of the original font that Fontlab creates
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, splitfn
from silfont.ufo import Ufont
import os, shutil, glob

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'filename'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_fixfontlab.log'})]

def doit(args) :

    fontname = args.ifont
    logger = args.logger
    params = args.paramsobj

    # Locate the oldest backup
    (path, base, ext) = splitfn(fontname)
    backuppath = os.path.join(path, base + ".*-*" + ext) # Backup has date/time added in format .yymmdd-hhmm
    backups = glob.glob(backuppath)
    if len(backups) == 0:
        logger.log("No backups found matching %s so no changes made to the font" % backuppath, "P")
        return
    backupname = sorted(backups)[0] # Choose the oldest backup - date/time format sorts alphabetically

    # Reset groups.plist, kerning.plist and any layerinfo.plist(s) from backup ufo
    for filename in ["groups.plist", "kerning.plist"]:
        bufullname = os.path.join(backupname, filename)
        ufofullname = os.path.join(fontname, filename)
        if os.path.exists(bufullname):
            try:
                shutil.copy(bufullname, fontname)
                logger.log(filename + " restored from backup", "P")
            except Exception as e:
                logger.log("Failed to copy %s to %s: %s" % (bufullname, fontname, str(e)), "S")
        elif os.path.exists(ufofullname):
            os.remove(ufofullname)
            logger.log(filename + " removed from ufo", "P")
    lifolders = []
    for ufoname in (fontname, backupname): # Find any layerinfo files in either ufo
        lis = glob.glob(os.path.join(ufoname, "*/layerinfo.plist"))
        for li in lis:
            (lifolder, dummy) = os.path.split(li)       # Get full path name for folder
            (dummy, lifolder) = os.path.split(lifolder) # Now take ufo name off the front
            if lifolder not in lifolders: lifolders.append(lifolder)
    for folder in lifolders:
        filename = os.path.join(folder, "layerinfo.plist")
        bufullname = os.path.join(backupname, filename)
        ufofullname = os.path.join(fontname, filename)
        if os.path.exists(bufullname):
            try:
                shutil.copy(bufullname, os.path.join(fontname, folder))
                logger.log(filename + " restored from backup", "P")
            except Exception as e:
                logger.log("Failed to copy %s to %s: %s" % (bufullname, fontname, str(e)), "S")
        elif os.path.exists(ufofullname):
            os.remove(ufofullname)
            logger.log(filename + " removed from ufo", "P")

    # Now open the fonts
    font = Ufont(fontname, params = params)
    backupfont = Ufont(backupname, params = params)

    fidel = ("openTypeGaspRangeRecords", "openTypeHeadFlags", "openTypeHheaCaretOffset", "openTypeOS2Selection",
             "postscriptBlueFuzz", "postscriptBlueScale", "postscriptBlueShift", "postscriptForceBold",
             "postscriptIsFixedPitch", "postscriptWeightName")
    libdel = ("com.fontlab.v2.tth", "com.typemytype.robofont.italicSlantOffset")
    fontinfo = font.fontinfo
    libplist = font.lib
    backupfi = backupfont.fontinfo
    backuplib = backupfont.lib

    # Delete keys that are not needed
    for key in fidel:
        if key in fontinfo:
            old = fontinfo.getval(key)
            fontinfo.remove(key)
            logchange(logger, " removed from fontinfo.plist. ", key, old, None)
    for key in libdel:
        if key in libplist:
            old = libplist.getval(key)
            libplist.remove(key)
            logchange(logger, " removed from lib.plist. ", key, old, None)

    # Correct other metadata:
    if "guidelines" in backupfi:
        fontinfo.setelem("guidelines",backupfi["guidelines"][1])
        logger.log("fontinfo guidelines copied from backup ufo", "I")
    elif "guidelines" in fontinfo:
        fontinfo.remove("guidelines")
        logger.log("fontinfo guidelines deleted - not in backup ufo", "I")
    if "italicAngle" in fontinfo and fontinfo.getval("italicAngle") == 0:
        fontinfo.remove("italicAngle")
        logger.log("fontinfo italicAngle removed since it was 0", "I")
    if "openTypeOS2VendorID" in fontinfo:
        old = fontinfo.getval("openTypeOS2VendorID")
        if len(old) < 4:
            new = "%-4s" % (old,)
            fontinfo.setval("openTypeOS2VendorID", "string", new)
            logchange(logger, " padded to 4 characters ", "openTypeOS2VendorID", "'%s'" % (old,) , "'%s'" % (new,))
    if "public.glyphOrder" in backuplib:
        libplist.setelem("public.glyphOrder",backuplib["public.glyphOrder"][1])
        logger.log("lib.plist public.glyphOrder copied from backup ufo", "I")
    elif "public.glyphOrder" in libplist:
        libplist.remove("public.glyphOrder")
        logger.log("libplist public.glyphOrder deleted - not in backup ufo", "I")


    # Now process glif level data
    updates = False
    for gname in font.deflayer:
        glyph = font.deflayer[gname]
        glines = glyph["guideline"]
        if glines:
            for gl in list(glines): glines.remove(gl) # Remove any existing glines
            updates = True
        buglines = backupfont.deflayer[gname]["guideline"] if gname in backupfont.deflayer else []
        if buglines:
            for gl in buglines: glines.append(gl) # Add in those from backup
            updates = True
    if updates:
        logger.log("Some updates to glif guidelines may have been made", "I")
        updates = False
    for layer in font.layers:
        if layer.layername == "public.background":
            for gname in layer:
                glyph = layer[gname]
                if glyph["advance"] is not None:
                    glyph.remove("advance")
                    updates = True
    if updates: logger.log("Some advance elements removed from public.background glifs", "I")
    font.write(fontname)
    return

def logchange(logger, logmess, key, old, new):
    oldstr = str(old) if len(str(old)) < 22 else str(old)[0:20] + "..."
    newstr = str(new) if len(str(new)) < 22 else str(new)[0:20] + "..."
    logmess = key + logmess
    if old is None:
        logmess = logmess + " New value: " + newstr
    else:
        if new is None:
            logmess = logmess + " Old value: " + oldstr
        else:
            logmess = logmess + " Old value: " + oldstr + ", new value: " + newstr
    logger.log(logmess, "I")

def cmd() : execute(None,doit, argspec)
if __name__ == "__main__": cmd()
