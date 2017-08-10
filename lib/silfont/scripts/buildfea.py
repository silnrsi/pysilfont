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
        self.all_aps = {}
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
            pass #TODO: read AP.xml into etree and process to extract anchors
            # may want to extract other info at the same time like class
            # and property values.

    def make_classes(self) :
        self.classes = {}
        for name, g in self.glyphs.items() :
            # pull off suffix and make classes
            # TODO: doesn't handle multiple suffices. Refactor for that.
            # TODO: handle ligatures
            pos = name.find('.')
            if pos > 0 :
                ext = name[pos+1:]
                base = name[:pos]
                if base in self.glyphs :
                    self.classes.setdefault("c_" + ext, []).append(name)
                    self.classes.setdefault("cno_" + ext, []).append(base)
            if g.is_mark :
                self.classes.setdefault('GDEF_marks', []).append(name)
            else :
                self.classes.setdefault('GDEF_bases', []).append(name)

    def make_marks(self) :
        for name, g in self.glyphs.items() :
            g.decide_if_mark()

    def append_classes(self, parser) :
        # normal glyph classes
        for name, c in self.classes.items() :
            gc = parser.ast.GlyphClass(0, None)
            for g in c :
                gc.append(g)
            gcd = parser.ast.GlyphClassDefinition(0, name, gc)
            parser.add_statement(gcd)
            parser.define_glyphclass(name, gc)

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
                    val = glyphs_w_pt
                else :
                    val = glyphs_w_pt[0]
                if not ap_nm.startswith("_"):
                    classdef = parser.ast.BaseClassDefinition(0, gc, anchor, parser.ast.GlyphClass(0, val))
                    bclassdef_lst.append(classdef)
                else:
                    classdef = parser.ast.MarkClassDefinition(0, gc, anchor, parser.ast.GlyphClass(0, val))
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
    ('-a', '--aps', {'help': 'Attachment Point database or .ufo file'}, {}),
    ('-i', '--input', {'help': 'Fea file to merge'}, {}),
    ('-o', '--output', {'help': 'Output fea file'}, {})
]

def doit(args) :
    font = Font()
    if args.aps :
        font.readaps(args.aps)
    elif args.infile.endswith('.ufo') :
        font.readaps(args.infile)

    font.make_marks()
    font.make_classes()

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
