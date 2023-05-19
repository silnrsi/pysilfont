#!/usr/bin/env python3
__doc__ = '''Sync metadata across a family of fonts based on designspace files'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.ufo as UFO
import silfont.etutil as ETU
import os, datetime
import fontTools.designspaceLib as DSD
from xml.etree import ElementTree as ET

argspec = [
    ('primaryds', {'help': 'Primary design space file'}, {'type': 'filename'}),
    ('secondds', {'help': 'Second design space file', 'nargs': '?', 'default': None}, {'type': 'filename', 'def': None}),
    ('--complex', {'help': 'Indicates complex set of fonts rather than RIBBI', 'action': 'store_true', 'default': False},{}),
    ('-l','--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_sync.log'}),
    ('-n','--new', {'help': 'append "_new" to file names', 'action': 'store_true', 'default': False},{}) # For testing/debugging
    ]

def doit(args) :
    ficopyreq = ("ascender", "copyright", "descender", "familyName", "openTypeHheaAscender",
                  "openTypeHheaDescender", "openTypeHheaLineGap", "openTypeNameDescription", "openTypeNameDesigner",
                  "openTypeNameDesignerURL", "openTypeNameLicense", "openTypeNameLicenseURL",
                  "openTypeNameManufacturer", "openTypeNameManufacturerURL", "openTypeNamePreferredFamilyName",
                  "openTypeNameVersion", "openTypeOS2CodePageRanges", "openTypeOS2TypoAscender",
                  "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap", "openTypeOS2UnicodeRanges",
                  "openTypeOS2VendorID", "openTypeOS2WinAscent", "openTypeOS2WinDescent", "versionMajor",
                  "versionMinor")
    ficopyopt = ("openTypeNameSampleText", "postscriptFamilyBlues", "postscriptFamilyOtherBlues", "trademark",
                 "woffMetadataCredits", "woffMetadataDescription")
    fispecial = ("italicAngle", "openTypeOS2WeightClass", "openTypeNamePreferredSubfamilyName", "openTypeNameUniqueID",
                 "styleMapFamilyName", "styleMapStyleName", "styleName", "unitsPerEm")
    fiall = sorted(set(ficopyreq) | set(ficopyopt) | set(fispecial))
    firequired = ficopyreq + ("openTypeOS2WeightClass", "styleName", "unitsPerEm")
    libcopyreq = ("com.schriftgestaltung.glyphOrder", "public.glyphOrder", "public.postscriptNames")
    libcopyopt = ("public.skipExportGlyphs",)
    liball = sorted(set(libcopyreq) | set(libcopyopt))
    logger = args.logger
    complex = args.complex

    pds = DSD.DesignSpaceDocument()
    pds.read(args.primaryds)
    if args.secondds is not None:
        sds = DSD.DesignSpaceDocument()
        sds.read(args.secondds)
    else:
        sds = None
    # Extract weight mappings from axes
    pwmap = swmap = {}
    for (ds, wmap, name) in ((pds, pwmap, "primary"),(sds, swmap, "secondary")):
        if ds:
            rawmap = None
            for descriptor in ds.axes:
                if descriptor.name == "weight":
                    rawmap = descriptor.map
                    break
            if rawmap:
                for (cssw, xvalue) in rawmap:
                    wmap[int(xvalue)] = int(cssw)
            else:
                logger.log(f"No weight axes mapping in {name} design space", "W")

    # Process all the sources
    psource = None
    dsources = []
    for source in pds.sources:
        if source.copyInfo:
            if psource: logger.log('Multiple fonts with <info copy="1" />', "S")
            psource = Dsource(pds, source, logger, frompds=True, psource = True, args = args)
        else:
            dsources.append(Dsource(pds, source, logger, frompds=True, psource = False, args = args))
    if sds is not None:
        for source in sds.sources:
            dsources.append(Dsource(sds, source, logger, frompds=False,  psource = False, args=args))

    # Process values in psource
    fipval = {}
    libpval = {}
    changes = False
    reqmissing = False

    for field in fiall:
        pval = psource.fontinfo.getval(field) if field in psource.fontinfo else None
        oval = pval
        # Set values or do other checks for special cases
        if field == "italicAngle":
            if "italic" in psource.source.filename.lower():
                if pval is None or pval == 0 :
                    logger.log(f"{psource.source.filename}: Italic angle must be non-zero for italic fonts", "E")
            else:
                if pval is not None and pval != 0 :
                    logger.log(f"{psource.source.filename}: Italic angle must be zero for non-italic fonts", "E")
                pval = None
        elif field == "openTypeOS2WeightClass":
            desweight = int(psource.source.location["weight"])
            if desweight in pwmap:
                pval = pwmap[desweight]
            else:
                logger.log(f"Design weight {desweight} not in axes mapping so openTypeOS2WeightClass not updated", "I")
        elif field == "styleMapFamilyName":
            if not complex and pval is None: logger.log("styleMapFamilyName missing from primary font", "E")
        elif field == "styleMapStyleName":
            if not complex and pval not in ('regular', 'bold', 'italic', 'bold italic'):
                logger.log("styleMapStyleName must be 'regular', 'bold', 'italic', 'bold italic'", "E")
        elif field in ("styleName", "openTypeNamePreferredSubfamilyName"):
            pval = psource.source.styleName
        elif field == "openTypeNameUniqueID":
            nm = str(fipval["openTypeNameManufacturer"]) # Need to wrap with str() just in case missing from
            fn = str(fipval["familyName"]) # fontinfo so would have been set to None
            sn = psource.source.styleName
            pval = nm + ": " + fn + " " + sn + ": " + datetime.datetime.now().strftime("%Y")
        elif field == "unitsperem":
            if pval is None or pval <= 0: logger.log("unitsperem must be non-zero", "S")
        # After processing special cases, all required fields should have values
        if pval is None and field in firequired:
            reqmissing = True
            logger.log("Required fontinfo field " + field + " missing from " + psource.source.filename, "E")
        elif oval != pval:
            changes = True
            if pval is None:
                if field in psource.fontinfo: psource.fontinfo.remove(field)
            else:
                psource.fontinfo[field][1].text = str(pval)
            logchange(logger, f"{psource.source.filename}: {field} updated:", oval, pval)
        fipval[field] = pval
    if reqmissing: logger.log("Required fontinfo fields missing from " + psource.source.filename, "S")
    if changes:
        psource.fontinfo.setval("openTypeHeadCreated", "string",
                             datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        psource.write("fontinfo")

    for field in liball:
        pval = psource.lib.getval(field) if field in psource.lib else None
        if pval is None:
            if field in libcopyreq:
                logtype = "W" if field[0:7] == "public." else "I"
                logger.log("lib.plist field " + field + " missing from " + psource.source.filename, logtype)
        libpval[field] = pval

    # Now update values in other source fonts

    for dsource in dsources:
        logger.log("Processing " + dsource.ufodir, "I")
        fchanges = False
        for field in fiall:
            sval = dsource.fontinfo.getval(field) if field in dsource.fontinfo else None
            oval = sval
            pval = fipval[field]
            # Set values or do other checks for special cases
            if field == "italicAngle":
                if "italic" in dsource.source.filename.lower():
                    if sval is None or sval == 0:
                        logger.log(dsource.source.filename + ": Italic angle must be non-zero for italic fonts", "E")
                else:
                    if sval is not None and sval != 0:
                        logger.log(dsource.source.filename + ": Italic angle must be zero for non-italic fonts", "E")
                    sval = None
            elif field == "openTypeOS2WeightClass":
                desweight = int(dsource.source.location["weight"])
                if desweight in swmap:
                    sval = swmap[desweight]
                else:
                    logger.log(f"Design weight {desweight} not in axes mapping so openTypeOS2WeightClass not updated", "I")
            elif field == "styleMapStyleName":
                if not complex and sval not in ('regular', 'bold', 'italic', 'bold italic'):
                    logger.log(dsource.source.filename + ": styleMapStyleName must be 'regular', 'bold', 'italic', 'bold italic'", "E")
            elif field in ("styleName", "openTypeNamePreferredSubfamilyName"):
                sval = dsource.source.styleName
            elif field == "openTypeNameUniqueID":
                sn = dsource.source.styleName
                sval = nm + ": " + fn + " " + sn + ": " + datetime.datetime.now().strftime("%Y")
            else:
                sval = pval
            if oval != sval:
                if field == "unitsPerEm": logger.log("unitsPerEm inconsistent across fonts", "S")
                fchanges = True
                if sval is None:
                    dsource.fontinfo.remove(field)
                    logmess = " removed: "
                else:
                    logmess = " added: " if oval is None else " updated: "
                    # Copy value from primary.  This will add if missing.
                    dsource.fontinfo.setelem(field, ET.fromstring(ET.tostring(psource.fontinfo[field][1])))
                    # For fields where it is not a copy from primary...
                    if field in ("italicAngle", "openTypeNamePreferredSubfamilyName", "openTypeNameUniqueID",
                                 "openTypeOS2WeightClass", "styleName"):
                        dsource.fontinfo[field][1].text = str(sval)

                logchange(logger, dsource.source.filename + " " + field + logmess, oval, sval)

        lchanges = False
        for field in liball:
            oval = dsource.lib.getval(field) if field in dsource.lib else None
            pval = libpval[field]
            if oval != pval:
                lchanges = True
                if pval is None:
                    dsource.lib.remove(field)
                    logmess = " removed: "
                else:
                    dsource.lib.setelem(field, ET.fromstring(ET.tostring(psource.lib[field][1])))
                    logmess = " updated: "
                logchange(logger, dsource.source.filename + " " + field + logmess, oval, pval)

        if lchanges:
            dsource.write("lib")
            fchanges = True # Force fontinfo to update so openTypeHeadCreated is set
        if fchanges:
            dsource.fontinfo.setval("openTypeHeadCreated", "string",
                                    datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            dsource.write("fontinfo")

    logger.log("psfsyncmasters completed", "P")

class Dsource(object):
    def __init__(self, ds, source, logger, frompds, psource, args):
        self.ds = ds
        self.source = source
        self.logger = logger
        self.frompds = frompds # Boolean to say if came from pds
        self.newfile = "_new" if args.new else ""
        self.ufodir = source.path
        if not os.path.isdir(self.ufodir): logger.log(self.ufodir + " in designspace doc does not exist", "S")
        try:
            self.fontinfo = UFO.Uplist(font=None, dirn=self.ufodir, filen="fontinfo.plist")
        except Exception as e:
            logger.log("Unable to open fontinfo.plist in " + self.ufodir, "S")
        try:
            self.lib = UFO.Uplist(font=None, dirn=self.ufodir, filen="lib.plist")
        except Exception as e:
            if psource:
                logger.log("Unable to open lib.plist in " + self.ufodir, "E")
                self.lib = {} # Just need empty dict, so all vals will be set to None
            else:
                logger.log("Unable to open lib.plist in " + self.ufodir + "; creating empty one", "E")
                self.lib = UFO.Uplist()
                self.lib.logger=logger
                self.lib.etree = ET.fromstring("<plist>\n<dict/>\n</plist>")
                self.lib.populate_dict()
                self.lib.dirn = self.ufodir
                self.lib.filen = "lib.plist"

        # Process parameters with similar logic to that in ufo.py. primarily to create outparams for writeXMLobject
        libparams = {}
        params = args.paramsobj
        if "org.sil.pysilfontparams" in self.lib:
            elem = self.lib["org.sil.pysilfontparams"][1]
            if elem.tag != "array":
                logger.log("Invalid parameter XML lib.plist - org.sil.pysilfontparams must be an array", "S")
            for param in elem:
                parn = param.tag
                if not (parn in params.paramclass) or params.paramclass[parn] not in ("outparams", "ufometadata"):
                    logger.log(
                        "lib.plist org.sil.pysilfontparams must only contain outparams or ufometadata values: " + parn + " invalid",
                        "S")
                libparams[parn] = param.text
        # Create font-specific parameter set (with updates from lib.plist)  Prepend names with ufodir to ensure uniqueness if multiple fonts open
        params.addset(self.ufodir + "lib", "lib.plist in " + self.ufodir, inputdict=libparams)
        if "command line" in params.sets:
            params.sets[self.ufodir + "lib"].updatewith("command line", log=False)  # Command line parameters override lib.plist ones
        copyset = "main" if "main" in params.sets else "default"
        params.addset(self.ufodir, copyset=copyset)
        params.sets[self.ufodir].updatewith(self.ufodir + "lib", sourcedesc="lib.plist")
        self.paramset = params.sets[self.ufodir]
        # Validate specific parameters
        if sorted(self.paramset["glifElemOrder"]) != sorted(params.sets["default"]["glifElemOrder"]):
            logger.log("Invalid values for glifElemOrder", "S")
        # Create outparams based on values in paramset, building attriborders from separate attriborders.<type> parameters.
        self.outparams = {"attribOrders": {}}
        for parn in params.classes["outparams"]:
            value = self.paramset[parn]
            if parn[0:12] == 'attribOrders':
                elemname = parn.split(".")[1]
                self.outparams["attribOrders"][elemname] = ETU.makeAttribOrder(value)
            else:
                self.outparams[parn] = value
        self.outparams["UFOversion"] = 9 # Dummy value since not currently needed

    def write(self, plistn):
        filen = plistn + self.newfile + ".plist"
        self.logger.log("Writing updated " + plistn + ".plist to " + filen, "P")
        exists = True if os.path.isfile(os.path.join(self.ufodir, filen)) else False
        plist = getattr(self, plistn)
        UFO.writeXMLobject(plist, self.outparams, self.ufodir, filen, exists, fobject=True)


def logchange(logger, logmess, old, new):
    oldstr = str(old) if len(str(old)) < 22 else str(old)[0:20] + "..."
    newstr = str(new) if len(str(new)) < 22 else str(new)[0:20] + "..."
    if old is None:
        logmess = logmess + " New value: " + newstr
    else:
        if new is None:
            logmess = logmess + " Old value: " + oldstr
        else:
            logmess = logmess + " Old value: " + oldstr + ", new value: " + newstr
    logger.log(logmess, "W")
    # Extra verbose logging
    if len(str(old)) > 21 :
        logger.log("Full old value: " + str(old), "V")
    if len(str(new)) > 21 :
        logger.log("Full new value: " + str(new), "V")
    logger.log("Types: Old - " + str(type(old)) + ", New - " + str(type(new)), "V")


def cmd() : execute(None,doit, argspec)
if __name__ == "__main__": cmd()


''' *** Code notes ***

Does not check precision for float, since no float values are currently processed
   - see processnum in psfsyncmeta if needed later

'''
