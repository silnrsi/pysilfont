#!/usr/bin/env python3
__doc__ = '''Update the various font version fields'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.ufo as UFO
import re

argspec = [
    ('font',{'help': 'From font file'}, {'type': 'infont'}),
    ('newversion',{'help': 'Version string or increment', 'nargs': '?'}, {}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_setversion.log'})
    ]

otnvre = re.compile('Version (\d)\.(\d\d\d)( .+)?$')

def doit(args) :

    font = args.font
    logger = args.logger
    newversion = args.newversion


    fi = font.fontinfo
    otelem = fi["openTypeNameVersion"][1] if "openTypeNameVersion" in fi else None
    majelem = fi["versionMajor"][1] if "versionMajor" in fi else None
    minelem = fi["versionMinor"][1] if "versionMinor" in fi else None
    otnv = None if otelem is None else otelem.text
    vmaj = None if majelem is None else majelem.text
    vmin = None if minelem is None else minelem.text

    if otnv is None or vmaj is None or vmin is None : logger.log("At least one of openTypeNameVersion, versionMajor or versionMinor missing from fontinfo.plist", "S")

    if newversion is None:
        if otnvre.match(otnv) is None:
            logger.log("Current version is '" + otnv + "' which is non-standard", "E")
        else :
            logger.log("Current version is '" + otnv + "'", "P")
            (otmaj,otmin,otextrainfo) = parseotnv(otnv)
            if (otmaj, int(otmin)) != (vmaj,int(vmin)) :
                logger.log("openTypeNameVersion values don't match versionMajor (" + vmaj + ") and versionMinor (" + vmin + ")", "E")
    else:
        if newversion[0:1] == "+" :
            if otnvre.match(otnv) is None:
                logger.log("Current openTypeNameVersion is non-standard so can't be incremented: " + otnv , "S")
            else :
                (otmaj,otmin,otextrainfo) = parseotnv(otnv)
                if (otmaj, int(otmin)) != (vmaj,int(vmin)) :
                    logger.log("openTypeNameVersion (" + otnv + ") doesn't match versionMajor (" + vmaj + ") and versionMinor (" + vmin + ")", "S")
            # Process increment to versionMinor.  Note vmin is treated as 3 digit mpp where m and pp are minor and patch versions respectively
            increment = newversion[1:]
            if increment not in ("1", "0.001", ".001", "0.1", ".1") :
                logger.log("Invalid increment value - must be one of 1, 0.001, .001, 0.1 or .1", "S")
            increment = 100 if increment in ("0.1", ".1") else 1
            if (increment == 100 and vmin[0:1] == "9") or (increment == 1 and vmin[1:2] == "99") :
                logger.log("Version already at maximum so can't be incremented", "S")
            otmin = str(int(otmin) + increment).zfill(3)
        else :
            newversion = "Version " + newversion
            if otnvre.match(newversion) is None:
                logger.log("newversion format invalid - should be 'M.mpp' or 'M.mpp extrainfo'", "S")
            else :
                (otmaj,otmin,otextrainfo) = parseotnv(newversion)
        newotnv = "Version " + otmaj + "." + otmin + otextrainfo # Extrainfo already as leading space
        logger.log("Updating version from '" + otnv + "' to '" + newotnv + "'","P")

        # Update and write to disk
        otelem.text = newotnv
        majelem.text = otmaj
        minelem.text = otmin
        UFO.writeXMLobject(fi,font.outparams,font.ufodir, "fontinfo.plist" , True, fobject = True)

    return

def parseotnv(string) : # Returns maj, min and extrainfo
    m = otnvre.match(string) # Assumes string has already been tested for a match
    extrainfo = "" if m.group(3) is None else m.group(3)
    return (m.group(1), m.group(2), extrainfo)


def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
