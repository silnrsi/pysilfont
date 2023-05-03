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
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2021 SIL International (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from silfont.core import execute, splitfn
from xml.etree import ElementTree as ET
from silfont.ufo import Ufont
import os, glob
from difflib import ndiff

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
    logger.log(f"Opening backup font {backupname}", "P")
    bfont = Ufont(backupname, params=params)
    outufoname = os.path.join(path, base + ".tidied.ufo")

    fllayers = {} # Dictionary of flfont layers by layer name
    for layer in flfont.layers: fllayers[layer.layername] = layer

    for layer in bfont.layers:
        if layer.layername not in fllayers:
            logger.log(f"layer {layer.layername} missing", "E")
            continue
        fllayer = fllayers[layer.layername]
        glifchangecount = 0
        smoothchangecount = 0
        duplicatenodecount = 0
        compchangecount = 0
        for gname in layer:
            glif = layer[gname]
            glifchange = False
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
                    flpoints = flc["point"]
                    duplicatenode = False
                    smoothchanges = True
                    if len(points) != len(flpoints): # Contours must be different!
                        if len(flpoints) - len(points) == 1: # Look for duplicate node issue
                            (different, plus, minus) = sdiff(str(ET.tostring(points[0]).strip()), str(ET.tostring(flpoints[0]).strip()))
                            if ET.tostring(points[0]).strip() == ET.tostring(flpoints[-1]).strip(): # With duplicate node issue first point is appended to the end
                                if plus == "lin" and minus == "curv": # On first point curve changed to line.
                                    duplicatenode = True # Also still need check all the remaining points are the same
                                    break                # but next check does that
                        otherchange = True # Duplicate node issue above is only case where contour count can be different
                        break

                    firstpoint = True
                    for point in points:
                        flp = flpoints.pop(0)
                        if firstpoint and duplicatenode: # Ignore the first point since that will be different
                            firstpoint = False
                            continue
                        firstpoint = False
                        (different, plus, minus) = sdiff(str(ET.tostring(point).strip()), str(ET.tostring(flp).strip()))
                        if different: # points are different
                            if plus.strip() + minus.strip() == 'smooth="yes"':
                                smoothchanges = True # Only difference is addition or removal of smooth="yes"
                            else: # Other change to glif,so can't safely make changes
                                otherchange = True

                if (smoothchanges or duplicatenode) and not otherchange: # Only changes to contours in glif are known issues that should be reset
                    flcontours = iter(floutline.contours)
                    for contour in list(contours):
                        flcontour = next(flcontours)
                        outline.replaceobject(contour, flcontour, "contour")
                    if smoothchanges:
                        logger.log(f'Smooth changes made to {gname}', "I")
                        smoothchangecount += 1
                    if duplicatenode:
                        logger.log(f'Duplicate node changes made to {gname}', "I")
                        duplicatenodecount += 1
                    glifchange = True

                # Now need to move components to the front...
                components = outline.components
                if len(components) > 0 and len(contours) > 0 and list(outline)[0] == "contour":
                    oldcontours = list(contours) # Easiest way to 'move' components is to delete contours then append back at the end
                    for contour in oldcontours: outline.removeobject(contour, "contour")
                    for contour in oldcontours: outline.appendobject(contour, "contour")
                    logger.log(f'Component position changes made to {gname}', "I")
                    compchangecount += 1
                    glifchange = True
                if glifchange: glifchangecount += 1

        logger.log(f'{layer.layername}: {glifchangecount} glifs changed', 'P')
        logger.log(f'{layer.layername}: {smoothchangecount} changes due to smooth, {duplicatenodecount} due to duplicate nodes and {compchangecount} due to components position', "P")

    bfont.write(outufoname)
    return

def sdiff(before, after): # Returns strings with the differences between the supplited strings
    if before == after: return(False,"","") # First returned value is True if the strings are different
    diff = ndiff(before, after)
    plus = ""  # Plus will have the extra characters that are only in after
    minus = "" # Minus will have the characters missing from after
    for d in diff:
        if d[0] == "+": plus += d[2]
        if d[0] == "-": minus += d[2]
    return(True, plus, minus)

def cmd() : execute("UFO",doit, argspec)
if __name__ == "__main__": cmd()
