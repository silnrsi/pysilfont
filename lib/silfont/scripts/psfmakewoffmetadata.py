#!/usr/bin/env python
__doc__ = 'Make the WOFF metadata xml file based on input UFO (and optionally FONTLOG.txt)'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
import silfont.ufo as UFO

import re, os, datetime
from xml.etree import ElementTree as ET

argspec = [
    ('font', {'help': 'Source font file'}, {'type': 'infont'}),
    ('-n', '--primaryname', {'help': 'Primary Font Name', 'required': True}, {}),
    ('-i', '--orgid', {'help': 'orgId', 'required': True}, {}),
    ('-f', '--fontlog', {'help': 'FONTLOG.txt file', 'default': 'FONTLOG.txt'}, {'type': 'filename'}),
    ('-o', '--output', {'help': 'Override output file'}, {'type': 'filename', 'def': None}),
    ('--populateufowoff', {'help': 'Copy info from FONTLOG.txt to UFO', 'action': 'store_true', 'default': False},{}),
    ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile', 'def': '_makewoff.log'})]

def doit(args):
    font = args.font
    pfn = args.primaryname
    orgid = args.orgid
    logger = args.logger
    ofn = args.output

    # Find & process info required in the UFO

    fi = font.fontinfo

    ufofields = {}
    missing = None
    for field in ("versionMajor", "versionMinor", "openTypeNameManufacturer", "openTypeNameManufacturerURL",
                  "openTypeNameLicense", "copyright", "trademark"):
        if field in fi:
            ufofields[field] = fi[field][1].text
        elif field != 'trademark':      # trademark is no longer required
            missing = field if missing is None else missing + ", " + field
    if missing is not None: logger.log("Field(s) missing from fontinfo.plist: " + missing, "S")

    version = ufofields["versionMajor"] + "." + ufofields["versionMinor"].zfill(3)

    # Find & process WOFF fields if present in the UFO

    missing = None
    ufofields["woffMetadataDescriptionurl"] =  None
    ufowoff = {"woffMetadataCredits": "credits", "woffMetadataDescription": "text"} # Field, dict name
    for field in ufowoff:
        fival = fi.getval(field) if field in fi else None
        if fival is None:
            missing = field if missing is None else missing + ", " + field
            ufofields[field] = None
        else:
            ufofields[field] = fival[ufowoff[field]]
            if field == "woffMetadataDescription" and "url" in fival:
                ufofields["woffMetadataDescriptionurl"] = fival["url"]

    # Process --populateufowoff setting, if present
    if args.populateufowoff:
        if missing != "woffMetadataCredits, woffMetadataDescription":
            logger.log("Data exists in the UFO for woffMetadata - remove manually to reuse --populateufowoff", "S")

    if args.populateufowoff or missing is not None:
        if missing: logger.log("WOFF field(s) missing from fontinfo.plist will be generated from FONTLOG.txt: " + missing, "W")
        # Open the fontlog file
        try:
            fontlog = open(args.fontlog)
        except Exception as e:
            logger.log(f"Unable to open {args.fontlog}: {str(e)}", "S")
        # Parse the fontlog file
        (section, match) = readuntil(fontlog, ("Basic Font Information",))  # Skip until start of "Basic Font Information" section
        if match is None: logger.log("No 'Basic Font Information' section in fontlog", "S")
        (fldescription, match) = readuntil(fontlog, ("Information for C", "Acknowledgements"))  # Description ends when first of these sections is found
        fldescription = [{"text": fldescription}]
        if match == "Information for C": (section, match) = readuntil(fontlog, ("Acknowledgements",))  # If Info... section present then skip on to Acknowledgements
        if match is None: logger.log("No 'Acknowledgements' section in fontlog", "S")
        (acksection, match) = readuntil(fontlog, ("No match needed!!",))

        flcredits = []
        credit = {}
        acktype = ""
        flog2woff = {"N": "name", "E": "Not used", "W": "url", "D": "role"}
        for line in acksection.splitlines():
            if line == "":
                if acktype != "":  # Must be at the end of a credit section
                    if "name" in credit:
                        flcredits.append(credit)
                    else:
                        logger.log("Credit section found with no N: entry", "E")
                credit = {}
                acktype = ""
            else:
                match = re.match("^([NEWD]): (.*)", line)
                if match is None:
                    if acktype == "N": credit["name"] = credit["name"] + line  # Name entries can be multiple lines
                else:
                    acktype = match.group(1)
                    if acktype in credit:
                        logger.log("Multiple " + acktype + " entries found in a credit section", "E")
                    else:
                        credit[flog2woff[acktype]] = match.group(2)
        if flcredits == []: logger.log("No credits found in fontlog", "S")
        if args.populateufowoff:
            ufofields["woffMetadataDescription"] = fldescription # Force fontlog values to be used writing metadata.xml later
            ufofields["woffMetadataCredits"] = flcredits
            # Create xml strings and update fontinfo
            xmlstring = "<dict>" + \
                        "<key>text</key><array><dict>" + \
                        "<key>text</key><string>" + textprotect(fldescription[0]["text"]) + "</string>" + \
                        "</dict></array>" + \
                        "<key>url</key><string>https://software.sil.org/</string>"\
                        "</dict>"
            fi.setelem("woffMetadataDescription", ET.fromstring(xmlstring))

            xmlstring = "<dict><key>credits</key><array>"
            for credit in flcredits:
                xmlstring += '<dict><key>name</key><string>' + textprotect(credit["name"]) + '</string>'
                if "url" in credit: xmlstring += '<key>url</key><string>' + textprotect(credit["url"]) + '</string>'
                if "role" in credit: xmlstring += '<key>role</key><string>' + textprotect(credit["role"]) + '</string>'
                xmlstring += '</dict>'
            xmlstring += '</array></dict>'
            fi.setelem("woffMetadataCredits", ET.fromstring(xmlstring))

            fi.setval("openTypeHeadCreated", "string", datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            logger.log("Writing updated fontinfo.plist with values from FONTLOG.txt", "P")
            exists = True if os.path.isfile(os.path.join(font.ufodir, "fontinfo.plist")) else False
            UFO.writeXMLobject(fi, font.outparams, font.ufodir, "fontinfo.plist", exists, fobject=True)

    description = ufofields["woffMetadataDescription"]
    if description == None: description = fldescription
    credits = ufofields["woffMetadataCredits"]
    if credits == None : credits = flcredits

    # Construct output file name
    (folder, ufoname) = os.path.split(font.ufodir)
    filename = os.path.join(folder, pfn + "-WOFF-metadata.xml") if ofn is None else ofn
    try:
        file = open(filename, "w")
    except Exception as e:
        logger.log("Unable to open " + filename + " for writing:\n" + str(e), "S")
    logger.log("Writing to : " + filename, "P")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<metadata version="1.0">\n')
    file.write('  <uniqueid id="' + orgid + '.' + pfn + '.' + version + '" />\n')
    file.write('  <vendor name="' + attrprotect(ufofields["openTypeNameManufacturer"]) + '" url="'
               + attrprotect(ufofields["openTypeNameManufacturerURL"]) + '" />\n')
    file.write('  <credits>\n')
    for credit in credits:
        file.write('    <credit\n')
        file.write('      name="' + attrprotect(credit["name"]) + '"\n')
        if "url" in credit: file.write('      url="' + attrprotect(credit["url"]) + '"\n')
        if "role" in credit: file.write('      role="' + attrprotect(credit["role"]) + '"\n')
        file.write('    />\n')
    file.write('  </credits>\n')

    if ufofields["woffMetadataDescriptionurl"]:
        file.write(f'  <description url="{ufofields["woffMetadataDescriptionurl"]}">\n')
    else:
        file.write('  <description>\n')
    file.write('    <text lang="en">\n')
    for entry in description:
        for line in entry["text"].splitlines():
            file.write('      ' + textprotect(line) + '\n')
    file.write('    </text>\n')
    file.write('  </description>\n')

    file.write('  <license url="http://scripts.sil.org/OFL" id="org.sil.ofl.1.1">\n')
    file.write('    <text lang="en">\n')
    for line in ufofields["openTypeNameLicense"].splitlines(): file.write('      ' + textprotect(line) + '\n')
    file.write('    </text>\n')
    file.write('  </license>\n')

    file.write('  <copyright>\n')
    file.write('    <text lang="en">\n')
    for line in ufofields["copyright"].splitlines(): file.write('      ' + textprotect(line) + '\n')
    file.write('    </text>\n')
    file.write('  </copyright>\n')

    if 'trademark' in ufofields:
        file.write('  <trademark>\n')
        file.write('    <text lang="en">' + textprotect(ufofields["trademark"]) + '</text>\n')
        file.write('  </trademark>\n')

    file.write('</metadata>')

    file.close()

def readuntil(file, texts):  # Read through file until line is in texts.  Return section up to there and the text matched
    skip = True
    match = None
    for line in file:
        line = line.strip()
        if skip:  # Skip underlines and blank lines at start of section
            if line == "" or line[0:5] == "-----":
                pass
            else:
                section = line
                skip = False
        else:
            for text in texts:
                if line[0:len(text)] == text: match = text
            if match: break
            section = section + "\n" + line
    while section[-1] == "\n": section = section[:-1]  # Strip blank lines at end
    return (section, match)

def textprotect(txt):  # Switch special characters in text to use &...; format
    txt = re.sub(r'&', '&amp;', txt)
    txt = re.sub(r'<', '&lt;', txt)
    txt = re.sub(r'>', '&gt;', txt)
    return txt

def attrprotect(txt):  # Switch special characters in text to use &...; format
    txt = re.sub(r'&', '&amp;', txt)
    txt = re.sub(r'<', '&lt;', txt)
    txt = re.sub(r'>', '&gt;', txt)
    txt = re.sub(r'"', '&quot;', txt)
    return txt

def cmd(): execute("UFO", doit, argspec)
if __name__ == "__main__": cmd()
