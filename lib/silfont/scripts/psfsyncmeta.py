#!/usr/bin/env python
from __future__ import unicode_literals
'''Sync metadata accross a family of fonts assuming standard UFO file naming'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from datetime import datetime
import silfont.ufo as UFO
import os
from xml.etree import ElementTree as ET

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_sync.log'}),
    ('-s','--single', {'help': 'Sync single UFO against master', 'action': 'store_true', 'default': False},{}),
    ('-m','--master', {'help': 'Master UFO to sync  single UFO against', 'nargs': '?' },{'type': 'infont', 'def': None}),
    ('-r','--reportonly', {'help': 'Report issues but no updating', 'action': 'store_true', 'default': False},{}),
    ('-n','--new', {'help': 'append "_new" to file/ufo names', 'action': 'store_true', 'default': False},{}),
    ('--normalize', {'help': 'output all the fonts to normalize them', 'action': 'store_true', 'default': False},{}),
    ]

def doit(args) :
    standardstyles = ["Regular", "Italic", "Bold", "BoldItalic"]
    finfoignore = ["openTypeHeadCreated", "openTypeOS2Panose", "postscriptBlueScale", "postscriptBlueShift",
                   "postscriptBlueValues", "postscriptOtherBlues", "postscriptStemSnapH", "postscriptStemSnapV", "postscriptForceBold"]
    libfields = ["public.postscriptNames", "public.glyphOrder", "com.schriftgestaltung.glyphOrder"]

    font = args.ifont
    logger = args.logger
    singlefont = args.single
    mfont = args.master
    newfile = "_new" if args.new else ""
    reportonly = args.reportonly
    updatemessage = " to be updated: " if reportonly else " updated: "
    params = args.paramsobj
    precision = font.paramset["precision"]

    # Increase screen logging level to W unless specific level supplied on command-line
    if not(args.quiet or "scrlevel" in params.sets["command line"]) : logger.scrlevel = "W"

    # Process UFO name
    (path,base) = os.path.split(font.ufodir)
    (base,ext) = os.path.splitext(base)
    if '-' not in base : logger.log("Non-standard UFO name - must be <family>-<style>", "S")
    (family,style) = base.split('-')

    styles = [style]
    fonts = {}
    fonts[style] = font

    # Process single and master settings
    if singlefont :
        if mfont :
            mastertext = "Master" # Used in log messages
        else : # Check against Regular font from same family
            mfont = openfont(params, path, family, "Regular")
            if mfont is None : logger.log("No regular font to check against - use -m to specify master font", "S")
            mastertext = "Regular"
            fonts["Regular"] =mfont
    else : # Supplied font must be Regular
        if mfont : logger.log("-m --master must only be used with -s --single", "S")
        if style != "Regular" : logger.log("Must specify a Regular font unless -s is used", "S")
        mastertext = "Regular"
        mfont = font

    # Check for required fields in master font
    mfinfo = mfont.fontinfo
    if "familyName" in mfinfo :
        spacedfamily = mfinfo["familyName"][1].text
    else:
        logger.log("No familyName field in " + mastertext, "S")
    if "openTypeNameManufacturer" in mfinfo :
        manufacturer = mfinfo["openTypeNameManufacturer"][1].text
    else:
        logger.log("No openTypeNameManufacturer field in " + mastertext, "S")
    mlib = mfont.lib

    # Open the remaining fonts in the family
    if not singlefont :
        for style in standardstyles :
            if not style in fonts :
                fonts[style] = openfont(params, path, family, style) # Will return None if font does not exist
                if fonts[style] is not None : styles.append(style)

    # Process fonts
    psuniqueidlist = []
    fieldscopied = False
    for style in styles :
        font = fonts[style]
        if font.UFOversion != "2" : logger.log("This script only works with UFO 2 format fonts","S")

        fontname = family + "-" + style
        spacedstyle = "Bold Italic" if style == "BoldItalic" else style
        spacedname = spacedfamily + " " + spacedstyle
        logger.log("************ Processing " + fontname, "P")

        ital = True if "Italic" in style else False
        bold = True if "Bold" in style else False

        # Process fontinfo.plist
        finfo=font.fontinfo
        fieldlist = list(set(finfo) | set(mfinfo)) # Need all fields from both to detect missing fields
        fchanged = False

        for field in fieldlist:
            action = None; issue = ""; newval = ""
            if field in finfo :
                elem = finfo[field][1]
                tag = elem.tag
                text = elem.text
                if text is None : text = ""
                if tag == "real" : text = processnum(text,precision)
            # Field-specific actions

            if field not in finfo :
                if field not in finfoignore : action = "Copyfield"
            elif field == "italicAngle" :
                if ital and text == "0" :
                    issue = "is zero"
                    action = "Warn"
                if not ital and text != "0" :
                    issue = "is non-zero"
                    newval = 0
                    action = "Update"
            elif field == "openTypeNameUniqueID" :
                newval = manufacturer + ": " + spacedname + ": " + datetime.now().strftime("%Y")
                if text != newval :
                    issue = "Incorrect value"
                    action = "Update"
            elif field == "openTypeOS2WeightClass" :
                if bold and text != "700" :
                    issue = "is not 700"
                    newval = 700
                    action = "Update"
                if not bold and text != "400" :
                    issue = "is not 400"
                    newval = 400
                    action = "Update"
            elif field == "postscriptFontName" :
                if text != fontname :
                    newval = fontname
                    issue = "Incorrect value"
                    action = "Update"
            elif field == "postscriptFullName" :
                if text != spacedname :
                    newval = spacedname
                    issue = "Incorrect value"
                    action = "Update"
            elif field == "postscriptUniqueID" :
                if text in psuniqueidlist :
                    issue = "has same value as another font: " + text
                    action = "Warn"
                else :
                    psuniqueidlist.append(text)
            elif field == "postscriptWeightName" :
                newval = 'bold' if bold else 'regular'
                if text != newval :
                    issue = "Incorrect value"
                    action = 'Update'
            elif field == "styleMapStyleName" :
                if text != spacedstyle.lower() :
                    newval = spacedstyle.lower()
                    issue = "Incorrect value"
                    action = "Update"
            elif field in ("styleName", "openTypeNamePreferredSubfamilyName") :
                if text != spacedstyle :
                    newval = spacedstyle
                    issue = "Incorrect value"
                    action = "Update"
            elif field in finfoignore :
                action = "Ignore"
            # Warn for fields in this font but not master
            elif field not in mfinfo :
                issue = "is in " + spacedstyle + " but not in " + mastertext
                action = "Warn"
            # for all other fields, sync values from master
            else :
                melem = mfinfo[field][1]
                mtag = melem.tag
                mtext = melem.text
                if mtext is None : mtext = ""
                if mtag is 'real' : mtext = processnum(mtext,precision)
                if tag in ("real", "integer", "string") :
                    if mtext != text :
                        issue = "does not match " + mastertext + " value"
                        newval = mtext
                        action = "Update"
                elif tag in ("true, false") :
                    if tag != mtag :
                        issue = "does not match " + mastertext + " value"
                        action = "FlipBoolean"
                elif tag == "array" : # Assume simple array with just values to compare
                    marray = mfinfo.getval(field)
                    array = finfo.getval(field)
                    if array != marray: action = "CopyArray"
                else : logger.log("Non-standard fontinfo field type in " + fontname, "X")

            # Now process the actions, create log messages etc
            if action is None or action == "Ignore" :
                pass
            elif action == "Warn" :
                logger.log(field + " needs manual correction: " + issue, "W")
            elif action == "Error" :
                logger.log(field + " needs manual correction: " + issue, "E")
            elif action in ("Update", "FlipBoolean", "Copyfield", "CopyArray") : # Updating actions
                fchanged = True
                message = field + updatemessage
                if action == "Update" :
                    message = message + issue + " Old: '" + text + "' New: '" + str(newval) + "'"
                    elem.text = newval
                elif action == "FlipBoolean" :
                    newval = "true" if tag == "false" else "false"
                    message = message + issue + " Old: '" + tag + "' New: '" + newval + "'"
                    finfo.setelem(field, ET.fromstring("<" + newval + "/>"))
                elif action == "Copyfield" :
                    message = message + "is missing so will be copied from " + mastertext
                    fieldscopied = True
                    finfo.addelem(field, ET.fromstring(ET.tostring(mfinfo[field][1])))
                elif action == "CopyArray" :
                    message = message + "Some values different Old: " + str(array) + " New: " + str(marray)
                    finfo.setelem(field, ET.fromstring(ET.tostring(melem)))
                logger.log(message, "W")
            else:
                logger.log("Uncoded action: " + action + " - oops", "X")

        # Process lib.plist - currently just public.postscriptNames and glyph order fields which are all simple dicts or arrays
        lib = font.lib
        lchanged = False

        for field in libfields:
            # Check the values
            action = None; issue = ""; newval = ""
            if field in mlib:
                if field in lib:
                    if lib.getval(field) != mlib.getval(field):  # will only work for arrays or dicts with simple values
                        action = "Updatefield"
                else:
                    action = "Copyfield"
            else:
                action = "Error" if field == ("public.GlyphOrder", "public.postscriptNames") else "Warn"
                issue = field + " not in " + mastertext + " lib.plist"

            # Process the actions, create log messages etc
            if action is None or action == "Ignore":
                pass
            elif action == "Warn":
                logger.log(field + " needs manual correction: " + issue, "W")
            elif action == "Error":
                logger.log(field + " needs manual correction: " + issue, "E")
            elif action in ("Updatefield", "Copyfield"):  # Updating actions
                lchanged = True
                message = field + updatemessage
                if action == "Copyfield":
                    message = message + "is missing so will be copied from " + mastertext
                    lib.addelem(field, ET.fromstring(ET.tostring(mlib[field][1])))
                elif action == "Updatefield":
                    message = message + "Some values different"
                    lib.setelem(field, ET.fromstring(ET.tostring(mlib[field][1])))
                logger.log(message, "W")
            else:
                logger.log("Uncoded action: " + action + " - oops", "X")

        # Now update on disk
        if not reportonly:
            if args.normalize:
                font.write(os.path.join(path, family + "-" + style + newfile + ".ufo"))
            else:  # Just update fontinfo and lib
                if fchanged:
                    filen = "fontinfo" + newfile + ".plist"
                    logger.log("Writing updated fontinfo to " + filen, "P")
                    exists = True if os.path.isfile(os.path.join(font.ufodir, filen)) else False
                    UFO.writeXMLobject(finfo, font.outparams, font.ufodir, filen, exists, fobject=True)
                if lchanged:
                    filen = "lib" + newfile + ".plist"
                    logger.log("Writing updated lib.plist to " + filen, "P")
                    exists = True if os.path.isfile(os.path.join(font.ufodir, filen)) else False
                    UFO.writeXMLobject(lib, font.outparams, font.ufodir, filen, exists, fobject=True)

    if fieldscopied :
        message = "After updating, UFOsyncMeta will need to be re-run to validate these fields" if reportonly else "Re-run UFOsyncMeta to validate these fields"
        logger.log("*** Some fields were missing and so copied from " + mastertext + ". " + message, "P")

    return


def openfont(params, path, family, style) : # Only try if directory esists
    ufodir = os.path.join(path,family+"-"+style+".ufo")
    font = UFO.Ufont(ufodir, params=params) if os.path.isdir(ufodir) else None
    return font


def processnum(text, precision) : # Apply same processing to numbers that normalization will
    if precision is not None:
        val = round(float(text), precision)
        if val == int(val) : val = int(val) # Removed trailing decimal .0
        text = str(val)
    return text


def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
