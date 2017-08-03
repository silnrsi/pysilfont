#!/usr/bin/python3
'Make features.fea file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken, Alan Ward'

from argparse import ArgumentParser
import silfont.ufo as ufo
from collections import OrderedDict
from silfont.feaplus import feaplus_parser
import fontTools.feaLib.ast as ast
import StringIO

from silfont.core import execute

class Glyph(object) :
    def __init__(self, name) :
        self.name = name
        self.anchors = {}
        self.is_mark = False

    def add_anchor(self, info) :
        self.anchors[info['name']] = complex(int(info['x']), int(info['y']))

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

    def prepend_classes(self, parser, count = 0) :
        # normal glyph classes
        for name, c in self.classes.items() :
            gc = parser.ast.GlyphClass(0, None)
            for g in c :
                gc.append(g)
            gcd = parser.ast.GlyphClassDefinition(0, name, gc)
            parser.doc_.statements.insert(count, gcd)
            parser.glyphclasses_.define(name, gc)
            count += 1
        return count

    def prepend_positions(self, parser, count = 0):
        # baseclasses and markclasses
        # should be similar to parser.parse_markClass in what structs are created
        #TODO: factor common code for baseClass and markClass generation into a method?
        doc_ = parser.doc_

        # create base and mark classes, add to fea file dicts and parser symbol table
        classdef_lst = []
        for ap_nm, glyphs_w_ap in self.all_aps.items() :
            # e.g. all glyphs with U AP
            if not ap_nm.startswith("_"):
                gc = parser.ast.BaseClass(ap_nm)
                if not hasattr(doc_, 'baseClasses') :
                    doc_.baseClasses = {}
                doc_.baseClasses[ap_nm] = gc
            else:
                gc = parser.ast.MarkClass(ap_nm)
                if not hasattr(doc_, 'markClasses') :
                    doc_.markClasses = {}
                doc_.markClasses[ap_nm] = gc
            parser.glyphclasses_.define(ap_nm, gc)

            # create lists of glyphs that use the same point (name and coordinates)
            # that can share a class definition
            anchor_cache = {}
            for g in glyphs_w_ap :
                p = g.anchors[ap_nm] # p is a tuple(glyph_name, pos)
                anchor_cache.setdefault(p, []).append(g.name)

            # create and add class definitions to base and mark classes
            for p, glyphs_w_pt in anchor_cache.items() :
                anchor = parser.ast.Anchor(0, None, p.real, p.imag, None, None, None)
                if len(glyphs_w_pt) > 1 :
                    if not ap_nm.startswith("_"):
                        classdef = parser.ast.BaseClassDefinition(0, gc, anchor, parser.ast.GlyphClass(0, glyphs_w_pt))
                    else:
                        classdef = parser.ast.MarkClassDefinition(0, gc, anchor, parser.ast.GlyphClass(0, glyphs_w_pt))
                else : # len == 1
                    if not ap_nm.startswith("_"):
                        classdef = parser.ast.BaseClassDefinition(0, gc, anchor, parser.ast.GlyphName(0, glyphs_w_pt[0]))
                    else:
                        classdef = parser.ast.MarkClassDefinition(0, gc, anchor, parser.ast.GlyphName(0, glyphs_w_pt[0]))
                classdef_lst.append(classdef)
                gc.addDefinition(classdef)

        # insert base classes before mark classes in fea file
        for classdef in classdef_lst:
            if type(classdef) == parser.ast.BaseClassDefinition:
                doc_.statements.insert(count, classdef)
                count += 1
        for classdef in classdef_lst:
            if type(classdef) == parser.ast.MarkClassDefinition:
                doc_.statements.insert(count, classdef)
                count += 1
        return count

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

    # parser the input
    if not args.input :
        args.input = StringIO.StringIO("")
    p = feaplus_parser(args.input, [])
    doc = p.parse() # returns an ast.FeatureFile

    first_index = font.prepend_classes(p)

    # prepend baseclasses and markclasses
    if args.input :
        first_index = font.prepend_positions(p, count=first_index)

    #TODO: conditional compilation, compare to fea, compile to ttf

    # output as doc.asFea()
    if args.output :
        with open(args.output, "w") as of :
            of.write(doc.asFea())

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
