#!/usr/bin/python3

from argparse import ArgumentParser
import silfont.ufo as ufo
from collections import OrderedDict
from silfont.feaplus import feaplus_parser
import fontTools.feaLib.ast as ast
import StringIO

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
            pass # read AP.xml into etree and process to extract anchors
            # may want to extract other info at the same time like class
            # and property values.

    def make_classes(self) :
        self.classes = {}
        for name, g in self.glyphs.items() :
            # pull off suffix and make classes
            # doesn't handle multiple suffices. Refactor for that.
            # handle ligatures
            pos = name.find('.')
            if pos > 0 :
                ext = name[pos+1:]
                base = name[:pos]
                if base in self.glyphs :
                    try: self.classes["c_" + ext].append(name)
                    except KeyError: self.classes["c_" + ext] = [name]
                    try: self.classes["cno_" + ext].append(base)
                    except KeyError: self.classes["cno_" + ext] = [base]
            if g.is_mark :
                try: self.classes['GDEF_marks'].append(name)
                except KeyError: self.classes['GDEF_marks'] = [name]
            else :
                try: self.classes['GDEF_bases'].append(name)
                except KeyError: self.classes['GDEF_bases'] = [name]

    def make_marks(self) :
        for name, g in self.glyphs.items() :
            g.decide_if_mark()

#    def prepend_classes(self, parser, count = 0) :
    def prepend_classes(self, parser, count = 0) :
        # normal classes
        #doc = parser.doc_
        for name, c in self.classes.items() :
            gc = parser.ast.GlyphClass(0, None)
            for g in c :
                gc.append(g)
            gcd = parser.ast.GlyphClassDefinition(0, name, gc)
            parser.doc_.statements.insert(count, gcd)
            count += 1
        return count

    def prepend_positions(self, parser, count = 0):
        # baseclasses and markclasses
        doc = parser.doc_
        for name, c in self.all_aps.items() :
            gc = parser.ast.BaseClass(name)
            if not hasattr(doc, 'baseClasses') :
                doc.baseClasses = {}
            doc.baseClasses[name] = gc
            parser.glyphclasses_.define(name, gc)
            # p is a tuple(glyph_name, pos)
            anchor_cache = {}
            for g in c :
                p = g.anchors[name]
                anchor_cache.setdefault(p, []).append(g.name)
            for p, gs in anchor_cache.items() :
                anchor = parser.ast.Anchor(0, None, p.real, p.imag, None, None, None)
                if len(gs) > 1 :
                    bcd = parser.ast.BaseClassDefinition(0, gc, anchor, parser.ast.GlyphClass(0, gs))
                else :
                    bcd = parser.ast.BaseClassDefinition(0, gc, anchor, parser.ast.GlyphName(0, gs[0]))
                doc.statements.insert(count, bcd)
                count += 1
        # repeat for markClasses
        return count

def cmd() :
    pass

parser = ArgumentParser()
parser.add_argument('infile', help="Input file")
parser.add_argument('-a','--aps',help="Attachment Point database or .ufo file")
parser.add_argument('-i','--input',help='Fea file to merge in')
parser.add_argument('-o','--output',help='Output fea file')
args = parser.parse_args()

# import pdb; pdb.set_trace()

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
doc = p.parse() # doc is an ast.FeatureFile

first_index = font.prepend_classes(p)

# prepend baseclasses and markclasses
if args.input :
    first_index = font.prepend_positions(p, count=first_index)

# output as doc.asFea()
if args.output :
    with open(args.output, "w") as of :
        of.write(doc.asFea())
