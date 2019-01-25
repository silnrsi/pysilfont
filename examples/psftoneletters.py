#!/usr/bin/env python
from __future__ import unicode_literals
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
    global glyphHeight, marginFlatLeft, marginPointLeft, marginFlatRight, marginPointRight, contourWidth, marginDotLeft, marginDotRight, dotSpacing, italicAngle, radius, strokeHeight, strokeDepth, contourGap, fakeBottom, dotRadius, dotBCP, contourGapDot, fakeBottomDot, anchorHeight, anchorOffset

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
    italicAngle = float(source["italicAngle"]) # angle of italic slant, 0 for upright

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

    anchorHeight = [ 0 , strokeDepth , (strokeDepth + contourGap) , (strokeDepth + contourGap * 2) , (strokeHeight - contourGap) , strokeHeight ]
    anchorOffset = 20   # hardcoded for now

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


def buildComp(f,g,pieces,ancLevelLeft,ancLevelMidLeft,ancLevelMidRight,ancLevelRight):

    g.clear()
    g.width = 0

    for p in pieces:
        g.appendComponent(p, (g.width, 0))
        g.width += f[p].width

    if ancLevelLeft > 0:
        anc_nm = "_TL"
        anc_x = adjItalX(0,anchorHeight[ancLevelLeft])
        if g.name[0:7] == 'TnStaff':
        	anc_x = anc_x - anchorOffset
        anc_y = anchorHeight[ancLevelLeft]
        g.appendAnchor(anc_nm, (anc_x, anc_y))

    if ancLevelMidLeft > 0:
        anc_nm = "_TL"
        anc_x = adjItalX(marginPointLeft + radius,anchorHeight[ancLevelMidLeft])
        anc_y = anchorHeight[ancLevelMidLeft]
        g.appendAnchor(anc_nm, (anc_x, anc_y))

    if ancLevelMidRight > 0:
        anc_nm = "TL"
        anc_x = adjItalX(g.width - marginPointRight - radius,anchorHeight[ancLevelMidRight])
        anc_y = anchorHeight[ancLevelMidRight]
        g.appendAnchor(anc_nm, (anc_x, anc_y))

    if ancLevelRight > 0:
        anc_nm = "TL"
        anc_x = adjItalX(g.width,anchorHeight[ancLevelRight])
        if g.name[0:7] == 'TnStaff':
        	anc_x = anc_x + anchorOffset
        anc_y = anchorHeight[ancLevelRight]
        g.appendAnchor(anc_nm, (anc_x, anc_y))


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
    g.width = 0

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


def rebuildTLComps(targetfont):

    f = targetfont

    # staff right
    for i in range(1,6):
        nameFull = 'TnStaffRt' + str(i)
        buildComp(f,f[nameFull],['TnLtrBar','TnLtrSpcFlatRight'],i,0,0,0)

    # staff right no outline
    for i in range(1,6):
        nameFull = 'TnStaffRt' + str(i) + 'no'
        buildComp(f,f[nameFull],['TnLtrSpcFlatRight'],i,0,0,0)

    # staff left
    for i in range(1,6):
        nameFull = 'TnStaffLft' + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcFlatLeft','TnLtrBar'],0,0,0,i)

    # staff left no outline
    for i in range(1,6):
        nameFull = 'TnStaffLft' + str(i) + 'no'
        buildComp(f,f[nameFull],['TnLtrSpcFlatLeft'],0,0,0,i)

    # contours right
    for i in range(1,6):
        for j in range(1,6):
            nameFull = 'TnContRt' + str(i) + str(j)
            segment = 'TnLtrSeg' + str(i) + str(j)
            buildComp(f,f[nameFull],['TnLtrSpcPointLeft',segment],0,i,0,j)

    # contours left
    for i in range(1,6):
        for j in range(1,6):
            nameFull = 'TnContLft' + str(i) + str(j)
            segment = 'TnLtrSeg' + str(i) + str(j)
            buildComp(f,f[nameFull],[segment,'TnLtrSpcPointRight'],i,0,j,0)

    # basic tone letters
    for i in range(1,6):
        nameFull = 'TnLtr' + str(i)
        segment = 'TnLtrSeg' + str(i) + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcPointLeft',segment,'TnLtrBar','TnLtrSpcFlatRight'],0,0,0,0)

    # basic tone letters no outline
    for i in range(1,6):
        nameFull = 'TnLtr' + str(i) + 'no'
        segment = 'TnLtrSeg' + str(i) + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcPointLeft',segment,'TnLtrSpcFlatRight'],0,i,0,0)

    # left stem tone letters
    for i in range(1,6):
        nameFull = 'LftStemTnLtr' + str(i)
        segment = 'TnLtrSeg' + str(i) + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcFlatLeft','TnLtrBar',segment,'TnLtrSpcPointRight'],0,0,0,0)

    # left stem tone letters no outline
    for i in range(1,6):
        nameFull = 'LftStemTnLtr' + str(i) + 'no'
        segment = 'TnLtrSeg' + str(i) + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcFlatLeft',segment,'TnLtrSpcPointRight'],0,0,i,0)

    # dotted tone letters
    for i in range(1,6):
        nameFull = 'DotTnLtr' + str(i)
        dot = 'TnLtrDot' + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcDotLeft',dot,'TnLtrSpcDotMiddle','TnLtrBar','TnLtrSpcFlatRight'],0,0,0,0)

    # dotted left stem tone letters
    for i in range(1,6):
        nameFull = 'DotLftStemTnLtr' + str(i)
        dot = 'TnLtrDot' + str(i)
        buildComp(f,f[nameFull],['TnLtrSpcFlatLeft','TnLtrBar','TnLtrSpcDotMiddle',dot,'TnLtrSpcDotRight'],0,0,0,0)


def doit(args):

    psffont = UFO.Ufont(args.ifont, params = args.paramsobj)
    rffont = OpenFont(args.ifont)
    outfont = args.ofont

    getParameters(psffont)

    updateTLPieces(rffont)
    rebuildTLComps(rffont)


    rffont.save(outfont)

    return

def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
