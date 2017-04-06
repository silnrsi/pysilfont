#!/usr/bin/python3

from argparse import ArgumentParser
import silfont.ufo as ufo
from collections import OrderedDict

class Glyph(object) :
    def __init__(self, name) :
        self.name = name
        self.anchors = {}
        self.is_mark = False

    def add_anchor(self, info) :
        self.anchors[info['name']] = complex(info['x'], info['y'])

    def decide_if_mark(self) :
        for a in self.anchors.keys() :
            if a.startswith("_") :
                self.is_mark = True
                break

class Font(object) :
    def __init__(self):
        self.glyphs = OrderedDict()
        self.classes = {}
        self.is_mark = False

    def readaps(self, filename) :
        if filename.endswith('.ufo') :
            f = ufo.Ufont(filename)
            for g in f.deflayer :
                glyph = Glyph(g.name)
                self.glyphs[g.name] = glyph
                if 'anchor' in g._contents :
                    for a in g._contents['anchor'] :
                        glyph.add_anchor(a.element.attrib)
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
                    self.classes["c_" + ext].append(name)
                    self.classes["cno_" + ext].append(base)
            if g.is_mark :
                self.classes['GDEF_marks'].append(name)
            else :
                self.classes['GDEF_bases'].append(name)

    def make_marks(self) :
        for name, g in self.glyphs.items() :
            g.decide_if_mark()

    def prepend_classes(self, parser, count = 0) :
        # normal classes
        doc = parser.doc_
        for name, c in self.classes.items() :
            gc = self.ast.GlyphClass(0)
            for g in c :
                gc.append(g)
            gcd = self.ast.GlyphClassDefinition(0, name, gc)
            doc.statements.insert(count, gcd)
            count += 1
        return count

    def prepend_positions(self, parser, count = 0):
        # baseclasses and markclasses
        doc = parser.doc_
        for name, c in self.baseclasses.items() :
            gc = self.ast.ast_BaseClass(name)
            parser.baseClasses[name] = gc
            parser.glyphClasses_.define(name, gc)
            # p is a tuple(glyph_name, pos)
            for p in c :
                anchor = self.ast.Anchor(0, None, p[1].real, p[1].imag, None, None, None)
                bcd = self.ast.ast_BaseClassDefinition(0, gc, name, anchor, [p[0]])
                doc.insert(count, bcd)
                count += 1
        # repeat for markClasses
        return count

parser = ArgumentParser()
parser.add_argument('infile', help="Input file")
parser.add_argument('-a','--aps',help="Attachment Point database or .ufo file")
parser.add_argument('-i','--input',help='Fea file to merge in')
parser.add_argument('-o','--output',help='Output fea file')
args = parser.parse_args()

font = Font()
if args.aps :
    font.readaps(args.aps)
elif args.infile.endswith('.ufo') :
    font.readaps(args.infile)

font.make_marks()
font.make_classes()

# parser the input
if args.input :
    p = feaplus_parser(args.input)
    doc = p.parse() # doc is an ast.FeatureFile
else :
    pass
    # make an empty doc here
# output as doc.asFea()

first_index = font.prepend_classes(p)
# prepend baseclasses and markclasses
first_index = font.prepend_positions(p, count=first_index)

if args.output :
    with open(args.output, "w") as of :
        of.write(doc.asFea())
