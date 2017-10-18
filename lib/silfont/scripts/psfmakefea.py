#!/usr/bin/python3
'Make features.fea file'
# TODO: add conditional compilation, compare to fea, compile to ttf
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken, Alan Ward'

import silfont.ufo as ufo
from collections import OrderedDict
from silfont.feaplus import feaplus_parser
from xml.etree import ElementTree as et
import fontTools.feaLib.ast as ast
import StringIO
import os

from silfont.core import execute

class Glyph(object) :
    def __init__(self, name) :
        self.name = name
        self.anchors = {}
        self.is_mark = False

    def add_anchor(self, info) :
        self.anchors[info['name']] = (int(info['x']), int(info['y']))

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

    def readaps(self, filename) :
        if filename.endswith('.ufo') :
            f = ufo.Ufont(filename)
            for g in f.deflayer :
                glyph = Glyph(g)
                self.glyphs[g] = glyph
                ufo_g = f.deflayer[g]
                if 'anchor' in ufo_g._contents :
                    for a in ufo_g._contents['anchor'] :
                        glyph.add_anchor(a.element.attrib)
                        self.all_aps.setdefault(a.element.attrib['name'], []).append(glyph)
        elif filename.endswith('.xml') :
            currGlyph = None
            currPoint = None
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
                        currPoint['x'] = elem.get('x', 0)
                        currPoint['y'] = elem.get('y', 0)
                elif event == 'end':
                    if elem.tag == 'point':
                        if currGlyph:
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
                ext = base[pos+1:]
                base = base[:pos]
                ext_class_nm = "c_" + ext
                base_glyph_nm = base + "." + ext
                base_glyph_lst = self.classes.setdefault(ext_class_nm, [])
                if base in self.glyphs and not base_glyph_nm in base_glyph_lst:
                    base_glyph_lst.append(base_glyph_nm)
                    self.classes.setdefault("cno_" + ext, []).append(base)
                pos = base.rfind('.')
            if g.is_mark :
                self.classes.setdefault('GDEF_marks', []).append(name)
            else :
                self.classes.setdefault('GDEF_bases', []).append(name)

    def make_marks(self) :
        for name, g in self.glyphs.items() :
            g.decide_if_mark()

    def append_classes(self, parser) :
        # normal glyph classes
        def sortkey(x):
            i = x[0].find('_')
            return (x[0][i:], x[0][:i], x[1]) if i > 0 else (x[0], "", x[1])

        for name, c in sorted(self.classes.items(), key=sortkey):
            gc = parser.ast.GlyphClass(0, None)
            for g in c :
                gc.append(g)
            gcd = parser.ast.GlyphClassDefinition(0, name, gc)
            parser.add_statement(gcd)
            parser.define_glyphclass(name, gcd)

    def append_positions(self, parser):
        # create base and mark classes, add to fea file dicts and parser symbol table
        bclassdef_lst = []
        mclassdef_lst = []
        for ap_nm, glyphs_w_ap in self.all_aps.items() :
            # e.g. all glyphs with U AP
            if not ap_nm.startswith("_"):
                gc = parser.set_baseclass(ap_nm)
            else:
                gc = parser.set_markclass(ap_nm)

            # create lists of glyphs that use the same point (name and coordinates)
            # that can share a class definition
            anchor_cache = {}
            for g in glyphs_w_ap :
                p = g.anchors[ap_nm]
                anchor_cache.setdefault(p, []).append(g.name)

            # create and add class definitions to base and mark classes
            for p, glyphs_w_pt in anchor_cache.items() :
                anchor = parser.ast.Anchor(0, None, p[0], p[1], None, None, None)
                if len(glyphs_w_pt) > 1 :
                    val = parser.ast.GlyphClass(0, glyphs_w_pt)
                else :
                    val = parser.ast.GlyphName(0, glyphs_w_pt[0])
                if not ap_nm.startswith("_"):
                    classdef = parser.ast.BaseClassDefinition(0, gc, anchor, val)
                    bclassdef_lst.append(classdef)
                else:
                    classdef = parser.ast.MarkClassDefinition(0, gc, anchor, val)
                    mclassdef_lst.append(classdef)
                gc.addDefinition(classdef)

        # insert base classes before mark classes in fea file
        for classdef in bclassdef_lst:
            parser.add_statement(classdef)
        for classdef in mclassdef_lst:
            parser.add_statement(classdef)

#TODO: provide more argument info
argspec = [
    ('infile', {'help': 'Input UFO or file'}, {}),
    ('-i', '--input', {'help': 'Fea file to merge'}, {}),
    ('-o', '--output', {'help': 'Output fea file'}, {}),
    ('-c', '--classfile', {'help': 'Classes file'}, {}),
    ('--classprops', {'help': 'Include property elements from classes file', 'action': 'store_true'}, {})
]

def doit(args) :
    font = Font()
    if args.infile :
        font.readaps(args.infile)

    font.make_marks()
    font.make_classes()
    if args.classfile:
        font.read_classes(args.classfile, classproperties = args.classprops)

    p = feaplus_parser(None, [])
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
