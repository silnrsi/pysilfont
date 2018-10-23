#!/usr/bin/python3
from __future__ import unicode_literals
'Make features.fea file'
# TODO: add conditional compilation, compare to fea, compile to ttf
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken, Alan Ward'

import silfont.ufo as ufo
from collections import OrderedDict
from silfont.feax_parser import feaplus_parser
from xml.etree import ElementTree as et

from silfont.core import execute

def getbbox(g):
    res = (65536, 65536, -65536, -65536)
    if g['outline'] is None:
        return (0, 0, 0, 0)
    for c in g['outline'].contours:
        for p in c['point']:
            if 'type' in p.attrib:      # any actual point counts
                x = float(p.get('x', '0'))
                y = float(p.get('y', '0'))
                res = (min(x, res[0]), min(y, res[1]), max(x, res[2]), max(y, res[3]))
    return res

class Glyph(object) :
    def __init__(self, name, advance=0, bbox=None) :
        self.name = name
        self.anchors = {}
        self.is_mark = False
        self.advance = int(float(advance))
        self.bbox = bbox or (0, 0, 0, 0)

    def add_anchor(self, info) :
        self.anchors[info['name']] = (int(float(info['x'])), int(float(info['y'])))

    def decide_if_mark(self) :
        for a in self.anchors.keys() :
            if a.startswith("_") :
                self.is_mark = True
                break

class Font(object) :
    def __init__(self):
        self.glyphs = OrderedDict()
        self.classes = {}
        self.all_aps = {}

    def readaps(self, filename, omitaps='', params = None) :
        omittedaps = set(omitaps.replace(',',' ').split())  # allow comma- and/or space-separated list
        if filename.endswith('.ufo') :
            f = ufo.Ufont(filename, params = params)
            self.fontinfo = f.fontinfo
            for g in f.deflayer :
                ufo_g = f.deflayer[g]
                advb = ufo_g['advance']
                adv = advb.width if advb is not None else 0
                bbox = getbbox(ufo_g)
                glyph = Glyph(g, advance=adv, bbox=bbox)
                self.glyphs[g] = glyph
                if 'anchor' in ufo_g._contents :
                    for a in ufo_g._contents['anchor'] :
                        if a.element.attrib['name'] not in omittedaps:
                            glyph.add_anchor(a.element.attrib)
                            self.all_aps.setdefault(a.element.attrib['name'], []).append(glyph)
        elif filename.endswith('.xml') :
            currGlyph = None
            currPoint = None
            self.fontinfo = {}
            for event, elem in et.iterparse(filename, events=('start', 'end')):
                if event == 'start':
                    if elem.tag == 'glyph':
                        name = elem.get('PSName', '')
                        if name:
                            currGlyph = Glyph(name)
                            self.glyphs[name] = currGlyph
                        currPoint = None
                    elif elem.tag == 'point':
                        currPoint = {'name' : elem.get('type', '')}
                    elif elem.tag == 'location' and currPoint is not None:
                        currPoint['x'] = int(elem.get('x', 0))
                        currPoint['y'] = int(elem.get('y', 0))
                    elif elem.tag == 'font':
                        n = elem.get('name', '')
                        x = n.split('-')
                        if len(x) == 2:
                            self.fontinfo['familyName'] = x[0]
                            self.fontinfo['openTypeNamePreferredFamilyName'] = x[0]
                            self.fontinfo['styleMapFamilyName'] = x[0]
                            self.fontinfo['styleName'] = x[1]
                            self.fontinfo['openTypeNamePreferredSubfamilyName'] = x[1]
                            self.fontinfo['postscriptFullName'] = "{0} {1}".format(*x)
                        self.fontinfo['postscriptFontName'] = n
                elif event == 'end':
                    if elem.tag == 'point':
                        if currGlyph and currPoint['name'] not in omittedaps:
                            currGlyph.add_anchor(currPoint)
                            self.all_aps.setdefault(currPoint['name'], []).append(currGlyph)
                        currPoint = None
                    elif elem.tag == 'glyph':
                        currGlyph = None

    def read_classes(self, fname, classproperties=False):
        doc = et.parse(fname)
        for c in doc.findall('.//class'):
            cl = []
            self.classes[c.get('name')] = cl  # assumes class does not already exist
            for e in c.get('exts', '').split() + [""]:
                for g in c.text.split():
                    if g+e in self.glyphs or (e == '' and g.startswith('@')):
                        cl.append(g+e)
        if not classproperties:
            return
        for c in doc.findall('.//property'):
            for e in c.get('exts', '').split() + [""]:
                for g in c.text.split():
                    if g+e in self.glyphs:
                        cname = c.get('name') + "_" + c.get('value')
                        self.classes.set_default(cname, []).append(g+e)
                    
    def make_classes(self) :
        for name, g in self.glyphs.items() :
            # pull off suffix and make classes
            # TODO: handle ligatures
            base = name
            pos = base.rfind('.')
            while pos > 0 :
                old_base = base
                ext = base[pos+1:]
                base = base[:pos]
                ext_class_nm = "c_" + ext
                if base in self.glyphs and old_base in self.glyphs:
                    glyph_lst = self.classes.setdefault(ext_class_nm, [])
                    if not old_base in glyph_lst:
                        glyph_lst.append(old_base)
                        self.classes.setdefault("cno_" + ext, []).append(base)
                pos = base.rfind('.')
            if g.is_mark :
                self.classes.setdefault('GDEF_marks', []).append(name)
            else :
                self.classes.setdefault('GDEF_bases', []).append(name)

    def make_marks(self) :
        for name, g in self.glyphs.items() :
            g.decide_if_mark()

    def order_classes(self):
        # return ordered list of classnames as desired for FEA

        # Start with alphabetical then correct:
        #   1. Put classes like "cno_whatever" adjacent to "c_whatever"
        #   2. Classes can be defined in terms of other classes but FEA requires that
        #      classes be defined before they can be referenced.

        def sortkey(x):
            key1 = 'c_' + x[4:] if x.startswith('cno_') else x
            return (key1, x)

        classes = sorted(self.classes.keys(), key=sortkey)
        links = {}  # key = classname; value = list of other classes that include this one
        counts = {} # key = classname; value = count of un-output classes that this class includes
        for name in classes:
            y = [c[1:] for c in self.classes[name] if c.startswith('@')]  #list of included classes
            counts[name] = len(y)
            for c in y:
                links.setdefault(c, []).append(name)

        outclasses = []
        while len(classes) > 0:
            foundone = False
            for name in classes:
                if counts[name] == 0:
                    foundone = True
                    # output this class
                    outclasses.append(name)
                    classes.remove(name)
                    # adjust counts of classes that include this one
                    if name in links:
                        for n in links[name]:
                            counts[n] -= 1
                    # It may now be possible to output some we skipped earlier,
                    # so start over from the begining of the list
                    break
            if not foundone:
                # all remaining classes include un-output classes and thus there is a loop somewhere
                raise ValueError("Class reference loop(s) found: " + ", ".join(classes))
        return outclasses

    def append_classes(self, parser) :
        # normal glyph classes
        for name in self.order_classes():
            gc = parser.ast.GlyphClass(None, location=None)
            for g in self.classes[name] :
                gc.append(g)
            gcd = parser.ast.GlyphClassDefinition(name, gc, location=None)
            parser.add_statement(gcd)
            parser.define_glyphclass(name, gcd)

    def _addGlyphsToClass(self, parser, glyphs, gc, anchor, definer):
        if len(glyphs) > 1 :
            val = parser.ast.GlyphClass(glyphs, location=None)
        else :
            val = parser.ast.GlyphName(glyphs[0], location=None)
        classdef = definer(gc, anchor, val, location=None)
        gc.addDefinition(classdef)
        parser.add_statement(classdef)

    def append_positions(self, parser):
        # create base and mark classes, add to fea file dicts and parser symbol table
        bclassdef_lst = []
        mclassdef_lst = []
        for ap_nm, glyphs_w_ap in self.all_aps.items() :
            # e.g. all glyphs with U AP
            if not ap_nm.startswith("_"):
                if any(not x.is_mark for x in glyphs_w_ap):
                    gcb = parser.set_baseclass(ap_nm)
                    parser.add_statement(gcb)
                if any(x.is_mark for x in glyphs_w_ap):
                    gcm = parser.set_baseclass(ap_nm + "_MarkBase")
                    parser.add_statement(gcm)
            else:
                gc = parser.set_markclass(ap_nm)

            # create lists of glyphs that use the same point (name and coordinates)
            # that can share a class definition
            anchor_cache = {}
            markanchor_cache = {}
            for g in glyphs_w_ap :
                p = g.anchors[ap_nm]
                if g.is_mark and not ap_nm.startswith("_"):
                    markanchor_cache.setdefault(p, []).append(g.name)
                else:
                    anchor_cache.setdefault(p, []).append(g.name)

            if ap_nm.startswith("_"):
                for p, glyphs_w_pt in anchor_cache.items():
                    anchor = parser.ast.Anchor(p[0], p[1], location=None)
                    self._addGlyphsToClass(parser, glyphs_w_pt, gc, anchor, parser.ast.MarkClassDefinition)
            else:
                for p, glyphs_w_pt in anchor_cache.items():
                    anchor = parser.ast.Anchor(p[0], p[1], location=None)
                    self._addGlyphsToClass(parser, glyphs_w_pt, gcb, anchor, parser.ast.BaseClassDefinition)
                for p, glyphs_w_pt in markanchor_cache.items():
                    anchor = parser.ast.Anchor(p[0], p[1], location=None)
                    self._addGlyphsToClass(parser, glyphs_w_pt, gcm, anchor, parser.ast.BaseClassDefinition)

#TODO: provide more argument info
argspec = [
    ('infile', {'help': 'Input UFO or file'}, {}),
    ('-i', '--input', {'help': 'Fea file to merge'}, {}),
    ('-o', '--output', {'help': 'Output fea file'}, {}),
    ('-c', '--classfile', {'help': 'Classes file'}, {}),
    ('--debug', {'help': 'Drop into pdb', 'action': 'store_true'}, {}),
    ('--classprops', {'help': 'Include property elements from classes file', 'action': 'store_true'}, {}),
    ('--omitaps', {'help': 'names of attachment points to omit (comma- or space-separated)', 'default': '', 'action': 'store'}, {})
]

def doit(args) :
    font = Font()
    if args.debug:
        import pdb; pdb.set_trace()
    if "checkfix" not in args.params:
        args.paramsobj.sets["main"]["checkfix"] = "None"
    if args.infile :
        font.readaps(args.infile, args.omitaps, args.paramsobj)

    font.make_marks()
    font.make_classes()
    if args.classfile:
        font.read_classes(args.classfile, classproperties = args.classprops)

    p = feaplus_parser(None, font.glyphs)
    p.fontinfo = font.fontinfo
    p.glyphs = font.glyphs
    doc_ufo = p.parse() # returns an empty ast.FeatureFile

    # Add goodies from the font
    font.append_classes(p)
    font.append_positions(p)

    # parse the input fea file
    if args.input :
        doc_fea = p.parse(args.input)
    else:
        doc_fea = doc_ufo

    # output as doc.asFea()
    if args.output :
        with open(args.output, "w") as of :
            of.write(doc_fea.asFea())

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
