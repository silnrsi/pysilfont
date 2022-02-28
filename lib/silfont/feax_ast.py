import ast as pyast
from fontTools.feaLib import ast
from fontTools.feaLib.ast import asFea
from fontTools.feaLib.error import FeatureLibError
import re, math

def asFea(g):
    if hasattr(g, 'asClassFea'):
        return g.asClassFea()
    elif hasattr(g, 'asFea'):
        return g.asFea()
    elif isinstance(g, tuple) and len(g) == 2:
        return asFea(g[0]) + "-" + asFea(g[1])   # a range
    elif g.lower() in ast.fea_keywords:
        return "\\" + g
    else:
        return g

ast.asFea = asFea
SHIFT = ast.SHIFT

def asLiteralFea(self, indent=""):
    Element.mode = 'literal'
    return self.asFea(indent=indent)
    Element.mode = 'flat'

ast.Element.asLiteralFea = asLiteralFea
ast.Element.mode = 'flat'

class ast_Comment(ast.Comment):
    def __init__(self, text, location=None):
        super(ast_Comment, self).__init__(text, location=location)
        self.pretext = ""
        self.posttext = ""

    def asFea(self, indent=""):
        return self.pretext + self.text + self.posttext

class ast_MarkClass(ast.MarkClass):
    # This is better fixed upstream in parser.parse_glyphclass_ to handle MarkClasses
    def asClassFea(self, indent=""):
        return "[" + " ".join(map(asFea, self.glyphs)) + "]"

class ast_BaseClass(ast_MarkClass) :
    def asFea(self, indent="") :
        return "@" + self.name + " = [" + " ".join(map(asFea, self.glyphs.keys())) + "];"

class ast_BaseClassDefinition(ast.MarkClassDefinition):
    def asFea(self, indent="") :
        # like base class asFea
        return ("# " if self.mode != 'literal' else "") + \
                "{}baseClass {} {} @{};".format(indent, self.glyphs.asFea(),
                                               self.anchor.asFea(), self.markClass.name)

class ast_MarkBasePosStatement(ast.MarkBasePosStatement):
    def asFea(self, indent=""):
        # handles members added by parse_position_base_ with feax syntax
        if isinstance(self.base, ast.MarkClassName): # flattens pos @BASECLASS mark @MARKCLASS
            res = ""
            if self.mode == 'literal':
                res += "pos base @{} ".format(self.base.markClass.name)
                res += " ".join("mark @{}".format(m.name) for m in self.marks)
                res += ";"
            else:
                for bcd in self.base.markClass.definitions:
                    if res != "":
                        res += "\n{}".format(indent)
                    res += "pos base {} {}".format(bcd.glyphs.asFea(), bcd.anchor.asFea())
                    res += "".join(" mark @{}".format(m.name) for m in self.marks)
                    res += ";"
        else: # like base class method
            res = "pos base {}".format(self.base.asFea())
            res += "".join(" {} mark @{}".format(a.asFea(), m.name) for a, m in self.marks)
            res += ";"
        return res

    def build(self, builder) :
        #TODO: do the right thing here (write to ttf?)
        pass

class ast_MarkMarkPosStatement(ast.MarkMarkPosStatement):
    # super class __init__() for reference
    # def __init__(self, location, baseMarks, marks):
    #     Statement.__init__(self, location)
    #     self.baseMarks, self.marks = baseMarks, marks

    def asFea(self, indent=""):
        # handles members added by parse_position_base_ with feax syntax
        if isinstance(self.baseMarks, ast.MarkClassName): # flattens pos @MARKCLASS mark @MARKCLASS
            res = ""
            if self.mode == 'literal':
                res += "pos mark @{} ".format(self.base.markClass.name)
                res += " ".join("mark @{}".format(m.name) for m in self.marks)
                res += ";"
            else:
                for mcd in self.baseMarks.markClass.definitions:
                    if res != "":
                        res += "\n{}".format(indent)
                    res += "pos mark {} {}".format(mcd.glyphs.asFea(), mcd.anchor.asFea())
                    for m in self.marks:
                        res += " mark @{}".format(m.name)
                    res += ";"
        else: # like base class method
            res = "pos mark {}".format(self.baseMarks.asFea())
            for a, m in self.marks:
                res += " {} mark @{}".format(a.asFea() if a else "<anchor NULL>", m.name)
            res += ";"
        return res

    def build(self, builder):
        # builder.add_mark_mark_pos(self.location, self.baseMarks.glyphSet(), self.marks)
        #TODO: do the right thing
        pass

class ast_CursivePosStatement(ast.CursivePosStatement):
    # super class __init__() for reference
    # def __init__(self, location, glyphclass, entryAnchor, exitAnchor):
    #     Statement.__init__(self, location)
    #     self.glyphclass = glyphclass
    #     self.entryAnchor, self.exitAnchor = entryAnchor, exitAnchor

    def asFea(self, indent=""):
        if isinstance(self.exitAnchor, ast.MarkClass): # pos cursive @BASE1 @BASE2
            res = ""
            if self.mode == 'literal':
                res += "pos cursive @{} @{};".format(self.glyphclass.name, self.exitAnchor.name)
            else:
                allglyphs = set(self.glyphclass.glyphSet())
                allglyphs.update(self.exitAnchor.glyphSet())
                for g in sorted(allglyphs):
                    entry = self.glyphclass.glyphs.get(g, None)
                    exit = self.exitAnchor.glyphs.get(g, None)
                    if res != "":
                        res += "\n{}".format(indent)
                    res += "pos cursive {} {} {};".format(g,
                                (entry.anchor.asFea() if entry else "<anchor NULL>"),
                                (exit.anchor.asFea() if exit else "<anchor NULL>"))
        else:
            res = super(ast_CursivePosStatement, self).asFea(indent)
        return res

    def build(self, builder) :
        #TODO: do the right thing here (write to ttf?)
        pass

class ast_MarkLigPosStatement(ast.MarkLigPosStatement):
    def __init__(self, ligatures, marks, location=None):
        ast.MarkLigPosStatement.__init__(self, ligatures, marks, location)
        self.classBased = False
        for l in marks:
            if l is not None:
                for m in l:
                    if m is not None and not isinstance(m[0], ast.Anchor):
                        self.classBased = True
                        break

    def build(self, builder):
        builder.add_mark_lig_pos(self.location, self.ligatures.glyphSet(), self.marks)

    def asFea(self, indent=""):
        if not self.classBased or self.mode == "literal":
            return super(ast_MarkLigPosStatement, self).asFea(indent)

        res = []
        for g in self.ligatures.glyphSet():
            comps = []
            for l in self.marks:
                onecomp = []
                if l is not None and len(l):
                    for a, m in l:
                        if not isinstance(a, ast.Anchor):
                            if g not in a.markClass.glyphs:
                                continue
                            left = a.markClass.glyphs[g].anchor.asFea()
                        else:
                            left = a.asFea()
                        onecomp.append("{} mark @{}".format(left, m.name))
                if not len(onecomp):
                    onecomp = ["<anchor NULL>"]
                comps.append(" ".join(onecomp))
            res.append("pos ligature {} ".format(asFea(g)) + ("\n"+indent+SHIFT+"ligComponent ").join(comps))
        return (";\n"+indent).join(res) + ";"

#similar to ast.MultipleSubstStatement
#one-to-many substitution, one glyph class is on LHS, multiple glyph classes may be on RHS
# equivalent to generation of one stmt for each glyph in the LHS class
# that's matched to corresponding glyphs in the RHS classes
#prefix and suffx are for contextual lookups and do not need processing
#replacement could contain multiple slots
#TODO: below only supports one RHS class?
class ast_MultipleSubstStatement(ast.Statement):
    def __init__(self, prefix, glyph, suffix, replacement, forceChain, location=None):
        ast.Statement.__init__(self, location)
        self.prefix, self.glyph, self.suffix = prefix, glyph, suffix
        self.replacement = replacement
        self.forceChain = forceChain
        lenglyphs = len(self.glyph.glyphSet())
        for i, r in enumerate(self.replacement) :
            if len(r.glyphSet()) == lenglyphs:
                self.multindex = i #first RHS slot with a glyph class
                break
        else:
            if lenglyphs > 1:
                raise FeatureLibError("No replacement class is of the same length as the matching class",
                                        location)
            else:
                self.multindex = 0;

    def build(self, builder):
        prefix = [p.glyphSet() for p in self.prefix]
        suffix = [s.glyphSet() for s in self.suffix]
        glyphs = self.glyph.glyphSet()
        replacements = self.replacement[self.multindex].glyphSet()
        lenglyphs = len(glyphs)
        for i in range(max(lenglyphs, len(replacements))) :
            builder.add_multiple_subst(
                self.location, prefix, glyphs[i if lenglyphs > 1 else 0], suffix,
                self.replacement[0:self.multindex] + [replacements[i]] + self.replacement[self.multindex+1:],
                self.forceChain)

    def asFea(self, indent=""):
        res = ""
        pres = (" ".join(map(asFea, self.prefix)) + " ") if len(self.prefix) else ""
        sufs = (" " + " ".join(map(asFea, self.suffix))) if len(self.suffix) else ""
        mark = "'" if len(self.prefix) or len(self.suffix) or self.forceChain else ""
        if self.mode == 'literal':
            res += "sub " + pres + self.glyph.asFea() + mark + sufs + " by "
            res += " ".join(asFea(g) for g in self.replacement) + ";"
            return res
        glyphs = self.glyph.glyphSet()
        replacements = self.replacement[self.multindex].glyphSet()
        lenglyphs = len(glyphs)
        count = max(lenglyphs, len(replacements))
        for i in range(count) :
            res += ("\n" + indent if i > 0 else "") + "sub " + pres
            res += asFea(glyphs[i if lenglyphs > 1 else 0]) + mark + sufs
            res += " by "
            res += " ".join(asFea(g) for g in self.replacement[0:self.multindex] + [replacements[i]] + self.replacement[self.multindex+1:])
            res += ";" 
        return res


# similar to ast.LigatureSubstStatement
# many-to-one substitution, one glyph class is on RHS, multiple glyph classes may be on LHS
# equivalent to generation of one stmt for each glyph in the RHS class
# that's matched to corresponding glyphs in the LHS classes
# it's unclear which LHS class should correspond to the RHS class
# prefix and suffx are for contextual lookups and do not need processing
# replacement could contain multiple slots
#TODO: below only supports one LHS class?
class ast_LigatureSubstStatement(ast.Statement):
    def __init__(self, prefix, glyphs, suffix, replacement,
                 forceChain, location=None):
        ast.Statement.__init__(self, location)
        self.prefix, self.glyphs, self.suffix = (prefix, glyphs, suffix)
        self.replacement, self.forceChain = replacement, forceChain
        lenreplace = len(self.replacement.glyphSet())
        for i, g in enumerate(self.glyphs):
            if len(g.glyphSet()) == lenreplace:
                self.multindex = i #first LHS slot with a glyph class
                break
        else:
            if lenreplace > 1:
                raise FeatureLibError("No class matches replacement class length", location)
            else:
                self.multindex = 0

    def build(self, builder):
        prefix = [p.glyphSet() for p in self.prefix]
        glyphs = [g.glyphSet() for g in self.glyphs]
        suffix = [s.glyphSet() for s in self.suffix]
        replacements = self.replacement.glyphSet()
        lenreplace = len(replacements.glyphSet())
        glyphs = self.glyphs[self.multindex].glyphSet()
        for i in range(max(len(glyphs), len(replacements))):
            builder.add_ligature_subst(
                self.location, prefix,
                self.glyphs[:self.multindex] + glyphs[i] + self.glyphs[self.multindex+1:],
                suffix, replacements[i if lenreplace > 1 else 0], self.forceChain)

    def asFea(self, indent=""):
        res = ""
        pres = (" ".join(map(asFea, self.prefix)) + " ") if len(self.prefix) else ""
        sufs = (" " + " ".join(map(asFea, self.suffix))) if len(self.suffix) else ""
        mark = "'" if len(self.prefix) or len(self.suffix) or self.forceChain else ""
        if self.mode == 'literal':
            res += "sub " + pres + " ".join(asFea(g)+mark for g in self.glyphs) + sufs + " by "
            res += self.replacements.asFea() + ";"
            return res
        glyphs = self.glyphs[self.multindex].glyphSet()
        replacements = self.replacement.glyphSet()
        lenreplace = len(replacements)
        count = max(len(glyphs), len(replacements))
        for i in range(count) :
            res += ("\n" + indent if i > 0 else "") + "sub " + pres
            res += " ".join(asFea(g)+mark for g in self.glyphs[:self.multindex] + [glyphs[i]] + self.glyphs[self.multindex+1:])
            res += sufs + " by "
            res += asFea(replacements[i if lenreplace > 1 else 0])
            res += ";"
        return res

class ast_AlternateSubstStatement(ast.Statement):
    def __init__(self, prefix, glyphs, suffix, replacements, location=None):
        ast.Statement.__init__(self, location)
        self.prefix, self.glyphs, self.suffix = (prefix, glyphs, suffix)
        self.replacements = replacements

    def build(self, builder):
        prefix = [p.glyphSet() for p in self.prefix]
        suffix = [s.glyphSet() for s in self.suffix]
        l = len(self.glyphs.glyphSet())
        for i, glyph in enumerate(self.glyphs.glyphSet()):
            replacement = self.replacements.glyphSet()[i::l]
            builder.add_alternate_subst(self.location, prefix, glyph, suffix,
                                    replacement)

    def asFea(self, indent=""):
        res = ""
        l = len(self.glyphs.glyphSet())
        for i, glyph in enumerate(self.glyphs.glyphSet()):
            if i > 0:
                res += "\n" + indent
            res += "sub "
            if len(self.prefix) or len(self.suffix):
                if len(self.prefix):
                    res += " ".join(map(asFea, self.prefix)) + " "
                res += asFea(glyph) + "'"    # even though we really only use 1
                if len(self.suffix):
                    res += " " + " ".join(map(asFea, self.suffix))
            else:
                res += asFea(glyph)
            res += " from "
            replacements = ast.GlyphClass(glyphs=self.replacements.glyphSet()[i::l], location=self.location)
            res += asFea(replacements)
            res += ";"
        return res

class ast_IfBlock(ast.Block):
    def __init__(self, testfn, name, cond, location=None):
        ast.Block.__init__(self, location=location)
        self.testfn = testfn
        self.name = name

    def asFea(self, indent=""):
        if self.mode == 'literal':
            res = "{}if{}({}) {{".format(indent, name, cond)
            res += ast.Block.asFea(self, indent=indent)
            res += indent + "}\n"
            return res
        elif self.testfn():
            return ast.Block.asFea(self, indent=indent)
        else:
            return ""


class ast_DoSubStatement(ast.Statement):
    def __init__(self, varnames, location=None):
        ast.Statement.__init__(self, location=location)
        self.names = varnames

    def items(self, variables):
        yield ((None, None),)

class ast_DoForSubStatement(ast_DoSubStatement):
    def __init__(self, varname, glyphs, location=None):
        ast_DoSubStatement.__init__(self, [varname], location=location)
        self.glyphs = glyphs.glyphSet()

    def items(self, variables):
        for g in self.glyphs:
            yield((self.names[0], g),)

def safeeval(exp):
    # no dunders in attribute names
    for n in pyast.walk(pyast.parse(exp)):
        v = getattr(n, 'id', "")
        # if v in ('_getiter_', '__next__'):
        #     continue
        if "__" in v:
            return False
    return True

class ast_DoLetSubStatement(ast_DoSubStatement):
    def __init__(self, varnames, expression, parser, location=None):
        ast_DoSubStatement.__init__(self, varnames, location=location)
        self.parser = parser
        if not safeeval(expression):
            expression='"Unsafe Expression"'
        self.expr = expression

    def items(self, variables):
        gbls = dict(self.parser.fns, **variables)
        try:
            v = eval(self.expr, gbls)
        except Exception as e:
            raise FeatureLibError(str(e) + " in " + self.expr, self.location)
        if self.names is None:      # in an if
            yield((None, v),)
        elif len(self.names) == 1:
            yield((self.names[0], v),)
        else:
            yield(zip(self.names, list(v) + [None] * (len(self.names) - len(v))))

class ast_DoIfSubStatement(ast_DoLetSubStatement):
    def __init__(self, expression, parser, block, location=None):
        ast_DoLetSubStatement.__init__(self, None, expression, parser, location=None)
        self.block = block

    def items(self, variables):
        (_, v) = list(ast_DoLetSubStatement.items(self, variables))[0][0]
        yield (None, (v if v else None),)

class ast_KernPairsStatement(ast.Statement):
    def __init__(self, kerninfo, location=None):
        super(ast_KernPairsStatement, self).__init__(location)
        self.kerninfo = kerninfo

    def asFea(self, indent=""):
        # return ("\n"+indent).join("pos {} {} {};".format(k1, round(v), k2) \
        #           for k1, x in self.kerninfo.items() for k2, v in x.items())
        coverage = set()
        rules = dict()

        # first sort into lists by type of rule
        for k1, x in self.kerninfo.items():
            for k2, v in x.items():
                # Determine pair kern type, where:
                #   'gg' = glyph-glyph, 'gc' = glyph-class', 'cg' = class-glyph, 'cc' = class-class
                ruleType = 'gc'[k1[0]=='@'] + 'gc'[k2[0]=='@']
                rules.setdefault(ruleType, list()).append([k1, round(v), k2])
                # for glyph-glyph rules, make list of first glyphs:
                if ruleType == 'gg':
                    coverage.add(k1)

        # Now assemble lines in order and convert gc rules to gg where possible:
        res = []
        for ruleType in ('gg', 'gc', 'cg', 'cc'):
            if ruleType != 'gc':
                res.extend(['pos {} {} {};'.format(k1, v, k2) for k1,v,k2 in rules[ruleType]])
            else:
                res.extend(['enum pos {} {} {};'.format(k1, v, k2) for k1, v, k2 in rules[ruleType] if k1 not in coverage])
                res.extend(['pos {} {} {};'.format(k1, v, k2) for k1, v, k2 in rules[ruleType] if k1 in coverage])

        return ("\n"+indent).join(res)

