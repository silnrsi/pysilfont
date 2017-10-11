from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser
from fontTools.feaLib.builder import Builder
from fontTools.feaLib.lexer import IncludingLexer
from fontTools.feaLib.ast import asFea
import StringIO

class ast_BaseClass(ast.MarkClass) :
    def asFea(self, indent="") :
        # should not be used since BaseClass is flattened to BaseClassDefinitions
        # in ast_MarkBasePosStatement.asFea and not output directly
        return ""

class ast_BaseClassDefinition(ast.MarkClassDefinition) :
    def asFea(self, indent="") :
        # like base class asFea
        return "# {}baseClass {} {} @{};".format(indent, self.glyphs.asFea(),
                                               self.anchor.asFea(), self.markClass.name)

class ast_MarkBasePosStatement(ast.MarkBasePosStatement):
    def asFea(self, indent=""):
        # handles members added by parse_position_base_ with feax syntax
        if isinstance(self.base, ast.MarkClassName): # flattens pos @BASECLASS mark @MARKCLASS
            res = ""
            for bcd in self.base.markClass.definitions:
                if res != "":
                    res += "\n{}".format(indent)
                res += "pos base {} {}".format(bcd.glyphs.asFea(), bcd.anchor.asFea())
                for m in self.marks:
                    res += " mark @{}".format(m.name)
                res += ";"
        else: # like base class method
            res = "pos base {}".format(self.base.asFea())
            for a, m in self.marks:
                res += " {} mark @{}".format(a.asFea(), m.name)
            res += ";"
        return res

    def build(self, builder) :
        #TODO: do the right thing here (write to ttf?)
        pass

#similar to ast.MultipleSubstStatement
#one-to-many substitution, one glyph class is on LHS, multiple glyph classes may be on RHS
# equivalent to generation of one stmt for each glyph in the LHS class
# that's matched to corresponding glyphs in the RHS classes
#prefix and suffx are for contextual lookups and do not need processing
#replacement could contain multiple slots
#TODO: below only supports one RHS class?
class ast_MultipleSubstStatement(ast.Statement):
    def __init__(self, location, prefix, glyph, suffix, replacement):
        ast.Statement.__init__(self, location)
        self.prefix, self.glyph, self.suffix = prefix, glyph, suffix
        self.replacement = replacement
        if len(self.glyph.glyphSet()) > 1 :
            for i, r in enumerate(self.replacement) :
                if len(r.glyphSet()) > 1 :
                    self.multindex = i #first RHS slot with a glyph class
                    break
        else :
            self.multindex = 0

    def build(self, builder):
        prefix = [p.glyphSet() for p in self.prefix]
        suffix = [s.glyphSet() for s in self.suffix]
        glyphs = self.glyph.glyphSet()
        replacements = self.replacement[self.multindex].glyphSet()
        for i in range(min(len(glyphs), len(replacements))) :
            builder.add_multiple_subst(
                self.location, prefix, glyphs[i], suffix,
                self.replacement[0:self.multindex] + [replacements[i]] + self.replacement[self.multindex+1:])

    def asFea(self, indent=""):
        res = ""
        pres = " ".join(map(asFea, self.prefix)) if len(self.prefix) else ""
        sufs = " ".join(map(asFea, self.suffix)) if len(self.suffix) else ""
        glyphs = self.glyph.glyphSet()
        replacements = self.replacement[self.multindex].glyphSet()
        for i in range(min(len(glyphs), len(replacements))) :
            res += ("\n" + indent if i > 0 else "") + "sub "
            if len(self.prefix) > 0 or len(self.suffix) > 0 :
                if len(self.prefix) :
                    res += pres + " "
                res += asFea(glyphs[i]) + "'"
                if len(self.suffix) :
                    res += " " + sufs
            else :
                res += asFea(glyphs[i])
            res += " by "
            res += " ".join(map(asFea, self.replacement[0:self.multindex] + [replacements[i]] + self.replacement[self.multindex+1:]))
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
    def __init__(self, location, prefix, glyphs, suffix, replacement,
                 forceChain):
        ast.Statement.__init__(self, location)
        self.prefix, self.glyphs, self.suffix = (prefix, glyphs, suffix)
        self.replacement, self.forceChain = replacement, forceChain
        if len(self.replacement.glyphSet()) > 1:
            for i, g in enumerate(self.glyphs):
                if len(g.glyphSet()) > 1:
                    self.multindex = i #first LHS slot with a glyph class
                    break
        else:
            self.multindex = 0

    def build(self, builder):
        prefix = [p.glyphSet() for p in self.prefix]
        glyphs = [g.glyphSet() for g in self.glyphs]
        suffix = [s.glyphSet() for s in self.suffix]
        replacements = self.replacement.glyphSet()
        glyphs = self.glyphs[self.multindex].glyphSet()
        for i in range(min(len(glyphs), len(replacements))):
            builder.add_ligature_subst(
                self.location, prefix,
                self.glyphs[:self.multindex] + glyphs[i] + self.glyphs[self.multindex+1:],
                suffix, replacements[i], self.forceChain)

    def asFea(self, indent=""):
        res = ""
        pres = " ".join(map(asFea, self.prefix)) if len(self.prefix) else ""
        sufs = " ".join(map(asFea, self.suffix)) if len(self.suffix) else ""
        glyphs = self.glyphs[self.multindex].glyphSet()
        replacements = self.replacement.glyphSet()
        for i in range(min(len(glyphs), len(replacements))) :
            res += ("\n" + indent if i > 0 else "") + "sub "
            if len(self.prefix) > 0 or len(self.suffix) > 0 :
                if len(self.prefix) :
                    res += pres + " "
                res += " ".join(asFea(g) + "'" for g in self.glyphs[:self.multindex] + [glyphs[i]] + self.glyphs[self.multindex+1:])
                if len(self.suffix) :
                    res += " " + sufs
            else :
                res += " ".join(map(asFea, self.glyphs[:self.multindex] + [glyphs[i]] + self.glyphs[self.multindex+1:]))
            res += " by "
            res += asFea(replacements[i])
            res += ";"
        return res


class feaplus_ast(object) :
    MarkBasePosStatement = ast_MarkBasePosStatement
    BaseClass = ast_BaseClass
    BaseClassDefinition = ast_BaseClassDefinition
    MultipleSubstStatement = ast_MultipleSubstStatement
    LigatureSubstStatement = ast_LigatureSubstStatement

    def __getattr__(self, name):
        return getattr(ast, name)

class feaplus_parser(Parser) :
    extensions = {
        'baseClass' : lambda s : s.parseBaseClass()
    }
    ast = feaplus_ast()

    def __init__(self, filename, glyphmap) :
        if filename is None :
            empty_file = StringIO.StringIO("")
            super(feaplus_parser, self).__init__(empty_file, glyphmap)
        else :
            super(feaplus_parser, self).__init__(filename, glyphmap)

    def parse(self, filename=None) :
        if filename is not None :
            self.lexer_ = IncludingLexer(filename)
            self.advance_lexer_(comments=True)
        return super(feaplus_parser, self).parse()

    # methods to limit layer violations
    def define_glyphclass(self, ap_nm, gc) :
        self.glyphclasses_.define(ap_nm, gc)

    def add_statement(self, val) :
        self.doc_.statements.append(val)

    def set_baseclass(self, ap_nm) :
        gc = self.ast.BaseClass(ap_nm)
        if not hasattr(self.doc_, 'baseClasses') :
            self.doc_.baseClasses = {}
        self.doc_.baseClasses[ap_nm] = gc
        self.define_glyphclass(ap_nm, gc)
        return gc

    def set_markclass(self, ap_nm) :
        gc = self.ast.MarkClass(ap_nm)
        if not hasattr(self.doc_, 'markClasses') :
            self.doc_.markClasses = {}
        self.doc_.markClasses[ap_nm] = gc
        self.define_glyphclass(ap_nm, gc)
        return gc


    # like base class parse_position_base_ & overrides it
    def parse_position_base_(self, enumerated, vertical):
        location = self.cur_token_location_
        self.expect_keyword_("base")
        if enumerated:
            raise FeatureLibError(
                '"enumerate" is not allowed with '
                'mark-to-base attachment positioning',
                location)
        base = self.parse_glyphclass_(accept_glyphname=True)
        if self.next_token_ == "<": # handle pos base [glyphs] <anchor> mark @MARKCLASS
            marks = self.parse_anchor_marks_()
        else: # handle pos base @BASECLASS mark @MARKCLASS; like base class parse_anchor_marks_
            marks = []
            while self.next_token_ == "mark": #TODO: is more than one 'mark' meaningful?
                self.expect_keyword_("mark")
                m = self.expect_markClass_reference_()
                marks.append(m)
        self.expect_symbol_(";")
        return self.ast.MarkBasePosStatement(location, base, marks)

    # like base class parseMarkClass
    # but uses BaseClass and BaseClassDefinition which subclass Mark counterparts
    def parseBaseClass(self):
        if not hasattr(self.doc_, 'baseClasses'):
            self.doc_.baseClasses = {}
        location = self.cur_token_location_
        glyphs = self.parse_glyphclass_(accept_glyphname=True)
        anchor = self.parse_anchor_()
        name = self.expect_class_name_()
        self.expect_symbol_(";")
        baseClass = self.doc_.baseClasses.get(name)
        if baseClass is None:
            baseClass = self.ast.BaseClass(name)
            self.doc_.baseClasses[name] = baseClass
            self.glyphclasses_.define(name, baseClass)
        bcdef = self.ast.BaseClassDefinition(location, baseClass, anchor, glyphs)
        baseClass.addDefinition(bcdef)
        return bcdef

    #similar to and overrides parser.parse_substitute_
    def parse_substitute_(self):
        assert self.cur_token_ in {"substitute", "sub", "reversesub", "rsub"}
        location = self.cur_token_location_
        reverse = self.cur_token_ in {"reversesub", "rsub"}
        old_prefix, old, lookups, values, old_suffix, hasMarks = \
            self.parse_glyph_pattern_(vertical=False)
        if any(values):
            raise FeatureLibError(
                "Substitution statements cannot contain values", location)
        new = []
        if self.next_token_ == "by":
            keyword = self.expect_keyword_("by")
            while self.next_token_ != ";":
                gc = self.parse_glyphclass_(accept_glyphname=True)
                new.append(gc)
        elif self.next_token_ == "from":
            keyword = self.expect_keyword_("from")
            new = [self.parse_glyphclass_(accept_glyphname=False)]
        else:
            keyword = None
        self.expect_symbol_(";")
        if len(new) is 0 and not any(lookups):
            raise FeatureLibError(
                'Expected "by", "from" or explicit lookup references',
                self.cur_token_location_)

        # GSUB lookup type 3: Alternate substitution.
        # Format: "substitute a from [a.1 a.2 a.3];"
        if keyword == "from":
            if reverse:
                raise FeatureLibError(
                    'Reverse chaining substitutions do not support "from"',
                    location)
            if len(old) != 1 or len(old[0].glyphSet()) != 1:
                raise FeatureLibError(
                    'Expected a single glyph before "from"',
                    location)
            if len(new) != 1:
                raise FeatureLibError(
                    'Expected a single glyphclass after "from"',
                    location)
            return self.ast.AlternateSubstStatement(
                location, old_prefix, old[0], old_suffix, new[0])

        num_lookups = len([l for l in lookups if l is not None])

        # GSUB lookup type 1: Single substitution.
        # Format A: "substitute a by a.sc;"
        # Format B: "substitute [one.fitted one.oldstyle] by one;"
        # Format C: "substitute [a-d] by [A.sc-D.sc];"
        if (not reverse and len(old) == 1 and len(new) == 1 and
                num_lookups == 0):
            glyphs = list(old[0].glyphSet())
            replacements = list(new[0].glyphSet())
            if len(replacements) == 1:
                replacements = replacements * len(glyphs)
            if len(glyphs) != len(replacements):
                raise FeatureLibError(
                    'Expected a glyph class with %d elements after "by", '
                    'but found a glyph class with %d elements' %
                    (len(glyphs), len(replacements)), location)
            return self.ast.SingleSubstStatement(
                location, old, new,
                old_prefix, old_suffix,
                forceChain=hasMarks
            )

        # GSUB lookup type 2: Multiple substitution.
        # Format: "substitute f_f_i by f f i;"
        if (not reverse and
                len(old) == 1 and len(new) > 1 and num_lookups == 0):
            return self.ast.MultipleSubstStatement(location, old_prefix, old[0], old_suffix, new)

        # GSUB lookup type 4: Ligature substitution.
        # Format: "substitute f f i by f_f_i;"
        if (not reverse and
                len(old) > 1 and len(new) == 1 and num_lookups == 0):
            return self.ast.LigatureSubstStatement(location, old_prefix, old, old_suffix, new[0], forceChain=hasMarks)

        # GSUB lookup type 8: Reverse chaining substitution.
        if reverse:
            if len(old) != 1:
                raise FeatureLibError(
                    "In reverse chaining single substitutions, "
                    "only a single glyph or glyph class can be replaced",
                    location)
            if len(new) != 1:
                raise FeatureLibError(
                    'In reverse chaining single substitutions, '
                    'the replacement (after "by") must be a single glyph '
                    'or glyph class', location)
            if num_lookups != 0:
                raise FeatureLibError(
                    "Reverse chaining substitutions cannot call named lookups",
                    location)
            glyphs = sorted(list(old[0].glyphSet()))
            replacements = sorted(list(new[0].glyphSet()))
            if len(replacements) == 1:
                replacements = replacements * len(glyphs)
            if len(glyphs) != len(replacements):
                raise FeatureLibError(
                    'Expected a glyph class with %d elements after "by", '
                    'but found a glyph class with %d elements' %
                    (len(glyphs), len(replacements)), location)
            return self.ast.ReverseChainSingleSubstStatement(
                location, old_prefix, old_suffix, old, new)

        # GSUB lookup type 6: Chaining contextual substitution.
        assert len(new) == 0, new
        rule = self.ast.ChainContextSubstStatement(
            location, old_prefix, old, old_suffix, lookups)
        return rule

