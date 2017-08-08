#!/usr/bin/env python
'''Creates Latin script tone letters (pitch contours)'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Victor Gaultney'

# Usage: psftoneletters ifont ofont
# Assumption is that the named tone letters already exist in the font,
# so this script is only to update (rebuild) them. New tone letter spaces
# in the font can be created with psfbuildcomp.py

# To Do
# Get parameters from lib.plist org.sil.lcg.toneLetters

# main input, output, and execution handled by pysilfont framework
from silfont.core import execute
import silfont.ufo as UFO

from robofab.world import OpenFont

from math import tan, radians, sqrt

suffix = '_toneletters'
argspec = [
   ('ifont',{'help': 'Input font file'}, {'type': 'filename'}),
   ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'filename', 'def': "_"+suffix}),
   ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': suffix+'log'})]


def getParameters(font):
    global glyphHeight, marginFlatLeft, marginPointLeft, marginFlatRight, marginPointRight, contourWidth, marginDotLeft, marginDotRight, dotSpacing, italicAngle, radius, strokeHeight, strokeDepth, contourGap, fakeBottom, dotRadius, dotBCP, contourGapDot, fakeBottomDot

    source = font.lib.getval("org.sil.lcg.toneLetters")

    strokeThickness = int(source["strokeThickness"]) # total width of stroke (ideally an even number)
    glyphHeight = int(source["glyphHeight"]) # height, including overshoot
    glyphDepth = int(source["glyphDepth"]) # depth - essentially overshoot (typically negative)
    marginFlatLeft = int(source["marginFlatLeft"]) # left sidebearing for straight bar
    marginPointLeft = int(source["marginPointLeft"]) # left sidebearing for endpoints
    marginFlatRight = int(source["marginFlatRight"]) # left sidebearing for straight bar
    marginPointRight = int(source["marginPointRight"]) # left sidebearing for endpoints
    contourWidth = int(source["contourWidth"]) # this is how wide the contour portions are, from the middle
                            # of one end to the other, in the horizontal axis. The actual
                            # bounding box of the contours would then be this plus the
                            # strokeThickness.
    marginDotLeft = int(source["marginDotLeft"]) # left sidebearing for dots
    marginDotRight = int(source["marginDotRight"]) # right sidebearing for dots
    dotSize = int(source["dotSize"]) # the diameter of the dot, normally 150% of the stroke weight
                            #  (ideally an even number)
    dotSpacing = int(source["dotSpacing"]) # the space between the edge of the dot and the
                            # edge of the expanded stroke
    italicAngle = int(source["italicAngle"]) # angle of italic slant, 0 for upright

    radius = round(strokeThickness / 2)
    strokeHeight = glyphHeight - radius                # for the unexpanded stroke
    strokeDepth = glyphDepth + radius
    strokeLength = strokeHeight - strokeDepth
    contourGap = round(strokeLength / 4)            # gap between contour levels
    fakeBottom = strokeDepth - contourGap            # a false 'bottom' for building contours

    dotRadius = round(dotSize / 2)                    # this gets redefined during nine tone process
    dotBCP = round((dotSize / 2) * .55)                # this gets redefined during nine tone process
    contourGapDot = round(( (glyphHeight - dotRadius) - (glyphDepth + dotRadius) ) / 4)
    fakeBottomDot = (glyphDepth + dotRadius) - contourGapDot


# drawing functions

def drawLine(glyph,startX,startY,endX,endY):

    dx = (endX - startX)                        # dx of original stroke
    dy = (endY - startY)                        # dy of original stroke
    len = sqrt( dx * dx + dy * dy )                # length of original stroke
    opp = round(dy * (radius / len))                    # offsets for on-curve points
    adj = round(dx * (radius / len))
    oppOff = round(opp * .55)                             # offsets for off-curve from on-curve
    adjOff = round(adj * .55)

    glyph.clearContours()

    pen = glyph.getPen()

    # print startX + opp, startY - adj

    pen.moveTo((startX + opp, startY - adj))
    pen.lineTo((endX + opp, endY - adj))        # first straight line

    bcp1x = endX + opp + adjOff
    bcp1y = endY - adj + oppOff
    bcp2x = endX + adj + oppOff
    bcp2y = endY + opp - adjOff
    pen.curveTo((bcp1x, bcp1y), (bcp2x, bcp2y), (endX + adj, endY + opp))

    bcp1x = endX + adj - oppOff
    bcp1y = endY + opp + adjOff
    bcp2x = endX - opp + adjOff
    bcp2y = endY + adj + oppOff
    pen.curveTo((bcp1x, bcp1y), (bcp2x, bcp2y), (endX - opp, endY + adj))

    pen.lineTo((startX - opp, startY + adj))    # second straight line

    bcp1x = startX - opp - adjOff
    bcp1y = startY + adj - oppOff
    bcp2x = startX - adj - oppOff
    bcp2y = startY - opp + adjOff
    pen.curveTo((bcp1x, bcp1y), (bcp2x, bcp2y), (startX - adj, startY - opp))

    bcp1x = startX - adj + oppOff
    bcp1y = startY - opp - adjOff
    bcp2x = startX + opp - adjOff
    bcp2y = startY - adj - oppOff
    pen.curveTo((bcp1x, bcp1y), (bcp2x, bcp2y), (startX + opp, startY - adj))
    # print startX + opp, startY - adj

    pen.closePath()


def drawDot(glyph,dotX,dotY):

    glyph.clearContours()

    pen = glyph.getPen()

    pen.moveTo((dotX, dotY - dotRadius))
    pen.curveTo((dotX + dotBCP, dotY - dotRadius), (dotX + dotRadius, dotY - dotBCP), (dotX + dotRadius, dotY))
    pen.curveTo((dotX + dotRadius, dotY + dotBCP), (dotX + dotBCP, dotY + dotRadius), (dotX, dotY + dotRadius))
    pen.curveTo((dotX - dotBCP, dotY + dotRadius), (dotX - dotRadius, dotY + dotBCP), (dotX - dotRadius, dotY))
    pen.curveTo((dotX - dotRadius, dotY - dotBCP), (dotX - dotBCP, dotY - dotRadius), (dotX, dotY - dotRadius))
    pen.closePath()


def adjItalX(aiX,aiY):
	newX = aiX + round(tan(radians(italicAngle)) * aiY)
	return newX


# updating functions

def updateTLPieces(targetfont):

    f = targetfont

    # set spacer widths
    f["TnLtrSpcFlatLeft"].width = marginFlatLeft + radius
    f["TnLtrSpcPointLeft"].width = marginPointLeft + radius - 1    # -1 corrects final sidebearing
    f["TnLtrSpcFlatRight"].width = marginFlatRight + radius
    f["TnLtrSpcPointRight"].width = marginPointRight + radius - 1    # -1 corrects final sidebearing
    f["TnLtrSpcDotLeft"].width = marginDotLeft + dotRadius
    f["TnLtrSpcDotMiddle"].width = dotRadius + dotSpacing + radius
    f["TnLtrSpcDotRight"].width = dotRadius + marginDotRight

    # redraw bar
    g = f["TnLtrBar"]
    drawLine(g,adjItalX(0,strokeDepth),strokeDepth,adjItalX(0,strokeHeight),strokeHeight)

    # redraw contours
    namePre = 'TnLtrSeg'
    for i in range(1,6):
        for j in range(1,6):

            nameFull = namePre + str(i) + str(j)

            if i == 5:                            # this deals with round off errors
                startLevel = strokeHeight
            else:
                startLevel = fakeBottom + i * contourGap
            if j == 5:
                endLevel = strokeHeight
            else:
                endLevel = fakeBottom + j * contourGap

            g = f[nameFull]
            g.width = contourWidth
            drawLine(g,adjItalX(1,startLevel),startLevel,adjItalX(contourWidth-1,endLevel),endLevel)


    # redraw dots
    namePre = 'TnLtrDot'
    for i in range(1,6):

        nameFull = namePre + str(i)

        if i == 5:                            # this deals with round off errors
            dotLevel = glyphHeight - dotRadius
        else:
            dotLevel = fakeBottomDot + i * contourGapDot

        g = f[nameFull]
        drawDot(g,adjItalX(0,dotLevel),dotLevel)


def doit(args):
    psffont = UFO.Ufont(args.ifont, params = args.paramsobj)
    rffont = OpenFont(args.ifont)
    outfont = args.ofont
    getParameters(psffont)
    updateTLPieces(rffont)
    rffont.save(outfont)

    return

def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
