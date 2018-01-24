#!/usr/bin/env python
'''Export fonts in a GlyphsApp file to UFOs'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

from silfont.core import execute

import glyphsLib
import silfont.ufo, os # Needed currently to read backup ufos from disk


argspec = [
    ('glyphsfont', {'help': 'Input font file'}, {'type': 'filename'}),
    ('masterdir', {'help': 'Output directory for masters'}, {}),
    ('--nofixes', {'help': 'Bypass code fixing data', 'action': 'store_true', 'default': False}, {}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_glyphs2ufo.log'})]


def doit(args):
    logger = args.logger
    logger.log("Creating UFO objects from GlyphsApp file", "I")
    ufos = glyphsLib.load_to_ufos(args.glyphsfont, propagate_anchors=False)

    # Extract directory name for use with backups
    (glyphsdir, filen) = os.path.split(args.glyphsfont)

    librestorekeys = ("org.sil.pysilfontparams", "org.sil.altLineMetrics", "org.sil.lcg.toneLetters",
                   "org.sil.lcg.transforms", "public.glyphOrder", "public.postscriptNames")
    libdeletekeys = ("UFOFormat", "com.schriftgestaltung.blueFuzz", "com.schriftgestaltung.blueScale",
                     "com.schriftgestaltung.blueShift")
    libdeleteempty = ("com.schriftgestaltung.DisplayStrings")

    inforestorekeys = ("openTypeHeadCreated", "openTypeNamePreferredFamilyName", "openTypeNamePreferredSubfamilyName",
                       "openTypeNameUniqueID", "openTypeOS2WeightClass", "openTypeOS2WidthClass", "postscriptFontName",
                       "postscriptFullName", "styleMapFamilyName", "styleMapStyleName", "styleName")
    integerkeys = ("openTypeOS2WeightClass", "openTypeOS2WidthClass")
    infodeleteempty = ("openTypeOS2Selection", "postscriptFamilyBlues", "postscriptFamilyOtherBlues",
                       "postscriptOtherBlues")
    infodelete = ("guidelelines", "openTypeOS2Type")

    for ufo in ufos:
        fontname = ufo.info.familyName.replace(" ", "") + "-" + ufo.info.styleName.replace(" ", "")
        # Fixes to the data
        if not args.nofixes:
            logger.log("Fixing data in " + fontname, "P")
            # lib.plist processing
            logger.log("Checking lib.plist", "P")

            libplist = ufo.lib

            # Process UFO.lib if present
            if "UFO.lib" in libplist:
                logger.log("UFOlib found in lib.plist for " + fontname + ". Values will be copied to root", "P")
                ul = libplist["UFO.lib"]
                # Copy fields from UFO.lib to root
                for key in ul:
                    if key in librestorekeys:
                        continue # They will be restored later
                    if key in libdeleteempty:
                        if ul[key] == "" :
                            logger.log("Emtpy field ignored: " + key, "I")
                            continue
                    if key in libdeletekeys:
                        logger.log(key + " ignored", "I")
                        continue
                    if key in ufo.lib:
                        current = ufo.lib[key]
                        logmess = " updated from UFO.lib. "
                    else:
                        current = None
                        logmess = " copied from UFO.lib. "
                    new = ul[key]
                    if current == new:
                        continue
                    else:
                        ufo.lib[key] = new
                        logchange(logger, logmess, key, current, new)
                del ufo.lib["UFO.lib"]
                logger.log("UFO.lib field deleted", "I")

            # Restore values from original UFOs, assuming nameed as <fontname>.ufo in same directory as input .gylphs file

            ufodir = os.path.join(glyphsdir,fontname+".ufo")
            try:
                origlibplist = silfont.ufo.Uplist(font=None, dirn=ufodir, filen="lib.plist")
            except Exception as e:
                logger.log("Unable to open lib.plist in " + ufodir + "; values will not be restored", "E")
                origlibplist = None

            if origlibplist is not None:
                for key in librestorekeys:
                    if key in origlibplist:
                        new = origlibplist.getval(key)
                        current = None if key not in ufo.lib else ufo.lib[key]
                        if current == new:
                            continue
                        else:
                            ufo.lib[key] = new
                            logchange(logger, " restored from backup ufo. ", key, current, new)

                for key in libdeletekeys:
                    if key in ufo.lib:
                        current = ufo.lib[key]
                        del ufo.lib[key]
                        logchange(logger, " deleted. ", key, current, None)

            # fontinfo.plist processing

            logger.log("Checking fontinfo.plist", "P")

            fontinfo = ufo.info
            try:
                origfontinfo = silfont.ufo.Uplist(font=None, dirn=ufodir, filen="fontinfo.plist")
            except Exception as e:
                logger.log("Unable to open fontinfo.plist in " + ufodir + "; values will not be restored", "E")
                origfontinfo = None

            if origfontinfo is not None:
                for key in inforestorekeys:
                    if key in origfontinfo:
                        new = origfontinfo.getval(key)
                        if key in integerkeys: new = int(new)
                        current = None if not hasattr(ufo.info, key) else  getattr(ufo.info, key)
                        if current == new:
                            continue
                        else:
                            setattr(ufo.info, key, new)
                            logchange(logger, " restored from backup ufo. ", key, current, new)

        # Write ufo out
        logger.log("Writing out " + fontname, "P")
        glyphsLib.write_ufo(ufo, args.masterdir)

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
    # Extra verbose logging
    if len(str(old)) > 21 :
        logger.log("Full old value: " + str(old), "V")
    if len(str(new)) > 21 :
        logger.log("Full new value: " + str(new), "V")
    logger.log("Types: Old - " + str(type(old)) + ", New - " + str(type(new)), "V")


def cmd(): execute(None, doit, argspec)
if __name__ == "__main__": cmd()
