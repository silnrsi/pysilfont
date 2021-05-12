#!/usr/bin/env python
__doc__ = '''Make changes to a backup UFO to match some changes made to another UFO by FontLab
When a UFO is first round-tripped through Fontlab 7, many changes are made including adding 'smooth="yes"' to many points
in glifs and removing it from others.  Also if components are after contours in a glif, then they get moved to before them.
These changes make initial comparisons hard and can mask other changes.  
This script takes the backup of the original font that Fontlab made and writes out a new version with contours changed 
to match those in the round-tripped UFO so a diff can then be done to look for other differences.
A glif is only changed if there are no other changes to contours.
If also moves components to match.
'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, splitfn
from xml.etree import ElementTree as ET
from silfont.ufo import Ufont
import os, glob

argspec = [
    ('ifont',{'help': 'post-fontlab ufo'}, {'type': 'infont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_tidyfontlab.log'})]

def doit(args) :

    flfont = args.ifont
    logger = args.logger
    params = args.paramsobj
    fontname = args.ifont.ufodir

    # Locate the oldest backup
    (path, base, ext) = splitfn(fontname)
    backuppath = os.path.join(path, base + ".*-*" + ext)  # Backup has date/time added in format .yymmdd-hhmm
    backups = glob.glob(backuppath)
    if len(backups) == 0:
        logger.log("No backups found matching %s so aborting..." % backuppath, "P")
        return
    backupname = sorted(backups)[0]  # Choose the oldest backup - date/time format sorts alphabetically
    bfont = Ufont(backupname, params=params)
    outufoname = os.path.join(path, base + ".tidied.ufo")

    fllayers = {} # Dictionary of flfont layers by layer name
    for layer in flfont.layers: fllayers[layer.layername] = layer

    for layer in bfont.layers:
        if layer.layername not in fllayers:
            logger.log(f"layer {layer.layername} missing", "E")
            continue
        fllayer = fllayers[layer.layername]
        smoothchangecount = 0
        compchangecount = 0
        for gname in layer:
            glif = layer[gname]
            flglif = fllayer[gname]
            if "outline" in glif and "outline" in flglif:
                changestomake = []
                otherchange = False
                outline = glif["outline"]
                floutline = flglif["outline"]
                contours = outline.contours
                if len(contours) != len(floutline.contours): break  # Different number so can't all be identical!
                flcontours = iter(floutline.contours)
                for contour in contours:
                    flc = next(flcontours)
                    points = contour["point"]
                    if len(points) != len(flc["point"]): # Contours must be different
                        otherchange = True
                        break
                    flpoints = iter(flc["point"])
                    for point in points:
                        flp = next(flpoints)
                        xml = ET.tostring(point).strip()
                        flxml = ET.tostring(flp).strip()
                        if xml != flxml: # points are different
                            if xml[:-2] + b'smooth="yes" />' == flxml or xml == flxml[:-2] + b'smooth="yes" />':
                                changestomake = True # Only difference is addition or removal of smooth="yes"
                            else: # Other change to glif,so can't safely make changes
                                otherchange = True

                if changestomake and not otherchange: # Only changes to contours in glif are addition(s) or removal(s) of smooth="yes"
                    flcontours = iter(floutline.contours)
                    for contour in list(contours):
                        flcontour = next(flcontours)
                        outline.replaceobject(contour, flcontour, "contour")
                    smoothchangecount += 1

                # Now need to move components to the front...
                components = outline.components
                if len(components) > 0 and len(contours) > 0 and list(outline)[0] == "contour":
                    oldcontours = list(contours) # Easiest way to 'move' components is to delete contours then append back at the end
                    for contour in oldcontours: outline.removeobject(contour, "contour")
                    for contour in oldcontours: outline.appendobject(contour, "contour")
                    compchangecount += 1

        logger.log(f'{layer.layername}: {smoothchangecount} glifs changed due to smooth and {compchangecount} glifs changed due to components position', "P")

    bfont.write(outufoname)
    return

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
