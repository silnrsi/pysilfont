#!/usr/bin/python
'IPython support for fonttools'

__all__ = ['displayGlyphs', 'loadFont', 'displayText', 'displayRaw']

from fontTools import ttLib
from fontTools.pens.basePen import BasePen
from fontTools.misc import arrayTools
from IPython.display import SVG, HTML

class SVGPen(BasePen) :

    def __init__(self, glyphSet, scale=1.0) :
        super(SVGPen, self).__init__(glyphSet);
        self.__commands = []
        self.__scale = scale

    def __str__(self) :
        return " ".join(self.__commands)

    def scale(self, pt) :
        return (pt[0] * self.__scale, pt[1] * self.__scale)

    def _moveTo(self, pt):
        self.__commands.append("M {0[0]} {0[1]}".format(self.scale(pt)))

    def _lineTo(self, pt):
        self.__commands.append("L {0[0]} {0[1]}".format(self.scale(pt)))

    def _curveToOne(self, pt1, pt2, pt3) :
        self.__commands.append("C {0[0]} {0[1]} {1[0]} {1[1]} {2[0]} {2[1]}".format(self.scale(pt1), self.scale(pt2), self.scale(pt3)))

    def _closePath(self) :
        self.__commands.append("Z")

    def clear(self) :
        self.__commands = []

def _svgheader():
    return '''<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
'''

def _bbox(f, gnames, points, scale=1):
    gset = f.glyphSet
    bbox = (0, 0, 0, 0)
    for i, gname in enumerate(gnames):
        if hasattr(points, '__len__') and i == len(points):
            points.append((bbox[2] / scale, 0))
        pt = points[i] if i < len(points) else (0, 0)
        g = gset[gname]._glyph
        if g is None or not hasattr(g, 'xMin') :
            gbox = (0, 0, 0, 0)
        else :
            gbox = (g.xMin * scale, g.yMin * scale, g.xMax * scale, g.yMax * scale)
        bbox = arrayTools.unionRect(bbox, arrayTools.offsetRect(gbox, pt[0] * scale, pt[1] * scale))
    return bbox

glyphsetcount = 0
def _defglyphs(f, gnames, scale=1):
    global glyphsetcount
    glyphsetcount += 1
    gset = f.glyphSet
    p = SVGPen(gset, scale)
    res = "<defs><g>\n"
    for gname in sorted(set(gnames)):
        res += '<symbol overflow="visible" id="{}_{}">\n'.format(gname, glyphsetcount)
        g = gset[gname]
        p.clear()
        g.draw(p)
        res += '<path style="stroke:none;" d="' + str(p) + '"/>\n</symbol>\n'
    res += "</g></defs>\n"
    return res

def loadFont(fname):
    return ttLib.TTFont(fname)

def displayGlyphs(f, gnames, points=None, scale=None):
    if not hasattr(gnames, '__len__') or isinstance(gnames, basestring):
        gnames = [gnames]
    if not hasattr(points, '__len__'):
        points = []
    if not hasattr(f, 'glyphSet'):
        f.glyphSet = f.getGlyphSet()
    res = _svgheader()
    if points is None:
        points = []
    bbox = _bbox(f, gnames, points, scale or 1)
    maxh = 100.
    height = bbox[3] - (bbox[1] if bbox[1] < 0 else 0)
    if scale is None and height > maxh:
        scale = maxh / height
        bbox = [x  * scale for x in bbox]
    res += _defglyphs(f, gnames, scale)
    res += '<g id="surface1" transform="matrix(1,0,0,-1,{},{})">\n'.format(-bbox[0], bbox[3])
    res += '  <rect x="{}" y="{}" width="{}" height="{}" style="fill:white;stroke:none"/>\n'.format(
        bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3])
    res += '  <g style="fill:black">\n'
    for i, gname in enumerate(gnames):
        pt = points[i] if i < len(points) else (0, 0)
        res += '    <use xlink:href="#{0}_{3}" x="{1}" y="{2}"/>\n'.format(gname, pt[0] * scale, pt[1] * scale, glyphsetcount)
    res += '  </g></g>\n</svg>\n'
    return SVG(data=res)
    #return res

def displayText(f, text, features = [], lang=None, dir="", script="", shapers="", size=0):
    import harfbuzz
    glyphs = harfbuzz.shape_text(f, text, features, lang, dir, script, shapers)
    gnames = []
    points = []
    x = 0
    y = 0
    for g in glyphs:
        gnames.append(f.getGlyphName(g.gid))
        points.append((x+g.offset[0], y+g.offset[1]))
        x += g.advance[0]
        y += g.advance[1]
    if size == 0:
        scale = None
    else:
        upem = f['head'].unitsPerEm
        scale = 4. * size / (upem * 3.)
    return displayGlyphs(f, gnames, points, scale=scale)

def displayRaw(text):
    res = "<html><body>"+text.encode('utf-8')+"</body></html>"
    return HTML(res)
