#!/usr/bin/env python
from __future__ import unicode_literals
'''Copy metadata between fonts in different (related) families
Usually run against the master (regular) font in each family then data synced within family afterwards'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.ufo as UFO
from xml.etree import cElementTree as ET

argspec = [
    ('fromfont',{'help': 'From font file'}, {'type': 'infont'}),
    ('tofont',{'help': 'To font file'}, {'type': 'infont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_copymeta.log'}),
    ('-r','--reportonly', {'help': 'Report issues but no updating', 'action': 'store_true', 'default': False},{})
    ]

def doit(args) :

    fields = ["copyright", "openTypeNameDescription", "openTypeNameDesigner", "openTypeNameDesignerURL", "openTypeNameLicense", # General feilds
                "openTypeNameLicenseURL", "openTypeNameManufacturer", "openTypeNameManufacturerURL", "openTypeOS2CodePageRanges",
                "openTypeOS2UnicodeRanges", "openTypeOS2VendorID", "trademark",
                "openTypeNameVersion", "versionMajor", "versionMinor", # Version fields
                "ascender", "descender", "openTypeHheaAscender", "openTypeHheaDescender", "openTypeHheaLineGap", # Design fields
                "openTypeOS2TypoAscender", "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap", "openTypeOS2WinAscent", "openTypeOS2WinDescent"]
    libfields = ["public.postscriptNames", "public.glyphOrder", "com.schriftgestaltung.glyphOrder"]

    fromfont = args.fromfont
    tofont = args.tofont
    logger = args.logger
    reportonly = args.reportonly

    updatemessage = " to be updated: " if reportonly else " updated: "
    precision = fromfont.paramset["precision"]
    # Increase screen logging level to W unless specific level supplied on command-line
    if not(args.quiet or "scrlevel" in args.paramsobj.sets["command line"]) : logger.scrlevel = "W"

    # Process fontinfo.plist
    ffi = fromfont.fontinfo
    tfi = tofont.fontinfo
    fupdated = False
    for field in fields:
        if field in ffi :
            felem = ffi[field][1]
            ftag = felem.tag
            ftext = felem.text
            if ftag is 'real' : ftext = processnum(ftext,precision)
            message = field + updatemessage

            if field in tfi : # Need to compare values to see if update is needed
                telem = tfi[field][1]
                ttag = telem.tag
                ttext = telem.text
                if ttag is 'real' : ttext = processnum(ttext,precision)

                if ftag in ("real", "integer", "string") :
                    if ftext != ttext :
                        if field == "openTypeNameLicense" : # Too long to display all
                            addmess = " Old: '" + ttext[0:80] + "...' New: '" + ftext[0:80] + "...'"
                        else: addmess = " Old: '" + ttext + "' New: '" + str(ftext) + "'"
                        telem.text = ftext
                        logger.log(message + addmess, "W")
                        fupdated = True
                elif ftag in ("true, false") :
                    if ftag != ttag :
                        fti.setelem(field, ET.fromstring("<" + ftag + "/>"))
                        logger.log(message + " Old: '" + ttag + "' New: '" + str(ftag) + "'", "W")
                        fupdated = True
                elif ftag == "array" : # Assume simple array with just values to compare
                    farray = []
                    for subelem in felem : farray.append(subelem.text)
                    tarray = []
                    for subelem in telem : tarray.append(subelem.text)
                    if farray != tarray :
                        tfi.setelem(field, ET.fromstring(ET.tostring(felem)))
                        logger.log(message + "Some values different Old: " + str(tarray) + " New: " + str(farray), "W")
                        fupdated = True
                else : logger.log("Non-standard fontinfo field type: "+ ftag + " in " + fontname, "S")
            else :
                tfi.addelem(field, ET.fromstring(ET.tostring(felem)))
                logger.log(message + "is missing from destination font so will be copied from source font", "W")
                fupdated = True
        else: # Field not in from font
            if field in tfi :
                logger.log( field +  " is missing from source font but present in destination font", "E")
            else :
                logger.log( field +  " is in neither font", "W")

    # Process lib.plist - currently just public.postscriptNames and glyph order fields which are all simple dicts or arrays
    flib = fromfont.lib
    tlib = tofont.lib
    lupdated = False
    for field in libfields:
        action = None
        if field in flib:
            if field in tlib:  # Need to compare values to see if update is needed
                if flib.getval(field) != tlib.getval(field):
                    action = "Updatefield"
            else:
                action = "Copyfield"
        else:
            action = "Error" if field == ("public.GlyphOrder", "public.postscriptNames") else "Warn"
            issue = field + " not in source font lib.plist"

        # Process the actions, create log messages etc
        if action is None or action == "Ignore":
            pass
        elif action == "Warn":
            logger.log(field + " needs manual correction: " + issue, "W")
        elif action == "Error":
            logger.log(field + " needs manual correction: " + issue, "E")
        elif action in ("Updatefield", "Copyfield"):  # Updating actions
            lupdated = True
            message = field + updatemessage
            if action == "Copyfield":
                message = message + "is missing so will be copied from source font"
                tlib.addelem(field, ET.fromstring(ET.tostring(flib[field][1])))
            elif action == "Updatefield":
                message = message + "Some values different"
                tlib.setelem(field, ET.fromstring(ET.tostring(flib[field][1])))
            logger.log(message, "W")
        else:
            logger.log("Uncoded action: " + action + " - oops", "X")

    # Now update on disk
    if not reportonly:
        if fupdated:
            logger.log("Writing updated fontinfo.plist", "P")
            UFO.writeXMLobject(tfi, tofont.outparams, tofont.ufodir, "fontinfo.plist", True, fobject=True)
        if lupdated:
            logger.log("Writing updated lib.plist", "P")
            UFO.writeXMLobject(tlib, tofont.outparams, tofont.ufodir, "lib.plist", True, fobject=True)

    return


def processnum(text, precision) : # Apply same processing to real numbers that normalization will
    if precision is not None:
        val = round(float(text), precision)
        if val == int(val) : val = int(val) # Removed trailing decimal .0
        text = str(val)
    return text


def cmd(): execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
