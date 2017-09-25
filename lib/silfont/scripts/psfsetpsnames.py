#!/usr/bin/env python
'''Add public.postscriptname to glif lib based on a csv file
- csv format glyphname,postscriptname'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute
from xml.etree import cElementTree as ET

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-i','--input',{'help': 'Input csv file'}, {'type': 'incsv', 'def': 'psnames.csv'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': 'setpsnames.log'})]

def doit(args) :
    font = args.ifont
    logger = args.logger
    incsv = args.input
    glyphlist = font.deflayer.keys() # List to check every glyph has a psname supplied

    dict = ET.Element("dict")
    line1 = True
    psnamepos = 1
    for line in incsv :
        if line1 : # Decide file format based on number of fields in line 1
            line1 = False
            numfields = len(line)
            if numfields > 2 : # line 1 should contain headings
                if "ps_name" in line :
                    psnamepos = line.index("ps_name")
                    if psnamepos == 0 : logger.log("First field must be glyph name, not ps_name","S")
                    incsv.numfields = numfields
                else:
                    logger.log("No ps_name field in csv headers")
                continue # Need to read first line with data!
            elif numfields == 2 :
                incsv.numfields = 2
            else:
                logger.log("Invalid first line in csv file", "S")
        glyphn = line[0]
        psname = line[psnamepos]
        if len(psname) == 0 or glyphn == psname:
        	continue	# No need to include cases where production name is blank or same as working name
        # Add to dict
        sub = ET.SubElement(dict,"key")
        sub.text = glyphn
        sub = ET.SubElement(dict,"string")
        sub.text = psname
        # Check if in font
        if glyphn in glyphlist :
            glyphlist.remove(glyphn)
        else :
            logger.log("No glyph in font for " + glyphn  + " on line " + str(incsv.line_num), "I")

    # Add to lib.plist
    if "lib" not in font.__dict__ : font.addfile("lib")
    font.lib.setelem("public.postscriptNames",dict)

    for glyphn in glyphlist : logger.log("No PS name in input file for font glyph " + glyphn,"I")

    return font

def cmd() : execute("UFO",doit,argspec)
if __name__ == "__main__": cmd()
