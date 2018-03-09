from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser
from fontTools.feaLib.lexer import IncludingLexer, Lexer
from fontTools.feaLib.error import FeatureLibError
import silfont.feax_ast as astx
import StringIO

class feaplus_ast(object) :
    MarkBasePosStatement = astx.ast_MarkBasePosStatement
    MarkMarkPosStatement = astx.ast_MarkMarkPosStatement
    CursivePosStatement = astx.ast_CursivePosStatement
    BaseClass = astx.ast_BaseClass
    MarkClass = astx.ast_MarkClass
    BaseClassDefinition = astx.ast_BaseClassDefinition
    MultipleSubstStatement = astx.ast_MultipleSubstStatement
    LigatureSubstStatement = astx.ast_LigatureSubstStatement

    def __getattr__(self, name):
        return getattr(ast, name) # retrieve undefined attrs from imported fontTools.feaLib ast module

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

    def resolve_glyphclass(self, ap_nm):
        return self.glyphclasses_.resolve(ap_nm)

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
        return self.ast.MarkBasePosStatement(base, marks, location=location)

    # like base class parse_position_mark_ & overrides it
    def parse_position_mark_(self, enumerated, vertical):
        location = self.cur_token_location_
        self.expect_keyword_("mark")
        if enumerated:
            raise FeatureLibError(
                '"enumerate" is not allowed with '
                'mark-to-mark attachment positioning',
                location)
        baseMarks = self.parse_glyphclass_(accept_glyphname=True)
        if self.next_token_ == "<": # handle pos mark [glyphs] <anchor> mark @MARKCLASS
            marks = self.parse_anchor_marks_()
        else: # handle pos mark @MARKCLASS mark @MARKCLASS; like base class parse_anchor_marks_
            marks = []
            while self.next_token_ == "mark": #TODO: is more than one 'mark' meaningful?
                self.expect_keyword_("mark")
                m = self.expect_markClass_reference_()
                marks.append(m)
        self.expect_symbol_(";")
        return self.ast.MarkMarkPosStatement(baseMarks, marks, location=location)

    def parse_position_cursive_(self, enumerated, vertical):
        location = self.cur_token_location_
        self.expect_keyword_("cursive")
        if enumerated:
            raise FeatureLibError(
                '"enumerate" is not allowed with '
                'cursive attachment positioning',
                location)
        glyphclass = self.parse_glyphclass_(accept_glyphname=True)
        if self.next_token_ == "<": # handle pos cursive @glyphClass <anchor entry> <anchor exit>
            entryAnchor = self.parse_anchor_()
            exitAnchor = self.parse_anchor_()
            self.expect_symbol_(";")
            return self.ast.CursivePosStatement(
                glyphclass, entryAnchor, exitAnchor, location=location)
        else: # handle pos cursive @baseClass @baseClass;
            mc = self.expect_markClass_reference_()
            return self.ast.CursivePosStatement(glyphclass.markClass, None, mc, location=location)

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
        bcdef = self.ast.BaseClassDefinition(baseClass, anchor, glyphs, location=location)
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
                old_prefix, old[0], old_suffix, new[0], location=location)

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
                old, new,
                old_prefix, old_suffix,
                forceChain=hasMarks, location=location
            )

        # GSUB lookup type 2: Multiple substitution.
        # Format: "substitute f_f_i by f f i;"
        if (not reverse and
                len(old) == 1 and len(new) > 1 and num_lookups == 0):
            return self.ast.MultipleSubstStatement(old_prefix, old[0], old_suffix, new, location=location)

        # GSUB lookup type 4: Ligature substitution.
        # Format: "substitute f f i by f_f_i;"
        if (not reverse and
                len(old) > 1 and len(new) == 1 and num_lookups == 0):
            return self.ast.LigatureSubstStatement(old_prefix, old, old_suffix, new[0],
                                                    forceChain=hasMarks, location=location)

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
                old_prefix, old_suffix, old, new, location=location)

        # GSUB lookup type 6: Chaining contextual substitution.
        assert len(new) == 0, new
        rule = self.ast.ChainContextSubstStatement(
            old_prefix, old, old_suffix, lookups, location=location)
        return rule

    def parse_glyphclass_(self, accept_glyphname):
        if (accept_glyphname and
                self.next_token_type_ in (Lexer.NAME, Lexer.CID)):
            glyph = self.expect_glyph_()
            return self.ast.GlyphName(glyph, location=self.cur_token_location_)
        if self.next_token_type_ is Lexer.GLYPHCLASS:
            self.advance_lexer_()
            gc = self.glyphclasses_.resolve(self.cur_token_)
            if gc is None:
                raise FeatureLibError(
                    "Unknown glyph class @%s" % self.cur_token_,
                    self.cur_token_location_)
            if isinstance(gc, self.ast.MarkClass):
                return self.ast.MarkClassName(gc, location=self.cur_token_location_)
            else:
                return self.ast.GlyphClassName(gc, location=self.cur_token_location_)

        self.expect_symbol_("[")
        location = self.cur_token_location_
        glyphs = self.ast.GlyphClass(location=location)
        while self.next_token_ != "]":
            if self.next_token_type_ is Lexer.NAME:
                glyph = self.expect_glyph_()
                location = self.cur_token_location_
                if '-' in glyph and glyph not in self.glyphNames_:
                    start, limit = self.split_glyph_range_(glyph, location)
                    glyphs.add_range(
                        start, limit,
                        self.make_glyph_range_(location, start, limit))
                elif self.next_token_ == "-":
                    start = glyph
                    self.expect_symbol_("-")
                    limit = self.expect_glyph_()
                    glyphs.add_range(
                        start, limit,
                        self.make_glyph_range_(location, start, limit))
                else:
                    glyphs.append(glyph)
            elif self.next_token_type_ is Lexer.CID:
                glyph = self.expect_glyph_()
                if self.next_token_ == "-":
                    range_location = self.cur_token_location_
                    range_start = self.cur_token_
                    self.expect_symbol_("-")
                    range_end = self.expect_cid_()
                    glyphs.add_cid_range(range_start, range_end,
                                         self.make_cid_range_(range_location,
                                                              range_start, range_end))
                else:
                    glyphs.append("cid%05d" % self.cur_token_)
            elif self.next_token_type_ is Lexer.GLYPHCLASS:
                self.advance_lexer_()
                gc = self.glyphclasses_.resolve(self.cur_token_)
                if gc is None:
                    raise FeatureLibError(
                        "Unknown glyph class @%s" % self.cur_token_,
                        self.cur_token_location_)
                # fix bug don't output class definition, just the name.
                if isinstance(gc, self.ast.MarkClass):
                    gcn = self.ast.MarkClassName(gc, location=self.cur_token_location_)
                else:
                    gcn = self.ast.GlyphClassName(gc, location=self.cur_token_location_)
                glyphs.add_class(gcn)
            else:
                raise FeatureLibError(
                    "Expected glyph name, glyph range, "
                    "or glyph class reference",
                    self.next_token_location_)
        self.expect_symbol_("]")
        return glyphs


