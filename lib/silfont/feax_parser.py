from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser
from fontTools.feaLib.lexer import IncludingLexer, Lexer
import silfont.feax_lexer as feax_lexer
from fontTools.feaLib.error import FeatureLibError
import silfont.feax_ast as astx
import StringIO, re

class feaplus_ast(object) :
    MarkBasePosStatement = astx.ast_MarkBasePosStatement
    MarkMarkPosStatement = astx.ast_MarkMarkPosStatement
    CursivePosStatement = astx.ast_CursivePosStatement
    BaseClass = astx.ast_BaseClass
    MarkClass = astx.ast_MarkClass
    BaseClassDefinition = astx.ast_BaseClassDefinition
    MultipleSubstStatement = astx.ast_MultipleSubstStatement
    LigatureSubstStatement = astx.ast_LigatureSubstStatement
    Variable = astx.ast_Variable
    IfBlock = astx.ast_IfBlock
    DoStatement = astx.ast_DoBlock
    DoForSubStatement = astx.ast_DoForSubStatement
    DoLetSubStatement = astx.ast_DoLetSubStatement
    DoIfSubStatement = astx.ast_DoIfSubStatement

    def __getattr__(self, name):
        return getattr(ast, name) # retrieve undefined attrs from imported fontTools.feaLib ast module

class feaplus_parser(Parser) :
    extensions = {
        'baseClass' : lambda s: s.parseBaseClass(),
        'ifclass' : lambda s: s.parseIfClass(),
        'ifinfo' : lambda s: s.parseIfInfo(),
        'do': lambda s: s.parseDoStatement_()
    }
    ast = feaplus_ast()

    def __init__(self, filename, glyphmap) :
        if filename is None :
            empty_file = StringIO.StringIO("")
            super(feaplus_parser, self).__init__(empty_file, glyphmap)
        else :
            super(feaplus_parser, self).__init__(filename, glyphmap)
        self.scope_ = astx.Scope()

    def parse(self, filename=None) :
        if filename is not None :
            self.lexer_ = feax_lexer.feax_IncludingLexer(filename)
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

    def parseIfClass(self):
        location = self.cur_token_location_
        self.expect_symbol_("(")
        if self.next_token_type_ is Lexer.GLYPHCLASS:
            self.advance_lexer_()
            def ifClassTest():
                gc = self.glyphclasses_.resolve(self.cur_token_)
                return gc is not None and len(gc.glyphSet())
            block = self.ast.IfBlock(ifClassTest, 'ifclass', '@'+self.cur_token_, location=location)
            self.expect_symbol_(")")
            import inspect      # oh this is so ugly!
            calledby = inspect.stack()[2][3]    # called through lambda since extension
            if calledby == 'parse_block_':
                self.parse_block_(block, False)
            else:
                self.parse_statements_block_(block)
            return block
        else:
            raise FeatureLibError("Syntax error missing glyphclass", location)

    def parseIfInfo(self):
        location = self.cur_token_location_
        self.expect_symbol_("(")
        name = self.expect_name_()
        self.expect_symbol_(",")
        reg = self.expect_string_()
        self.expect_symbol_(")")
        def ifInfoTest():
            s = self.fontinfo.get(name, "")
            return re.search(reg, s)
        block = self.ast.IfBlock(ifInfoTest, 'ifinfo', '{}, "{}"'.format(name, reg), location=location)
        import inspect      # oh this is so ugly! Instead caller should pass in context
        calledby = inspect.stack()[2][3]        # called through a lambda since extension
        if calledby == 'parse_block_':
            self.parse_block_(block, False)
        else:
            self.parse_statements_block_(block)
        return block
        
    def parse_statements_block_(self, block):
        self.expect_symbol_("{")
        statements = block.statements
        while self.next_token_ != "}" or self.cur_comments_:
            self.advance_lexer_(comments=True)
            if self.cur_token_type_ is Lexer.COMMENT:
                statements.append(
                    self.ast.Comment(self.cur_token_,
                                     location=self.cur_token_location_))
            elif self.is_cur_keyword_("include"):
                statements.append(self.parse_include_())
            elif self.cur_token_type_ is Lexer.GLYPHCLASS:
                statements.append(self.parse_glyphclass_definition_())
            elif self.is_cur_keyword_(("anon", "anonymous")):
                statements.append(self.parse_anonymous_())
            elif self.is_cur_keyword_("anchorDef"):
                statements.append(self.parse_anchordef_())
            elif self.is_cur_keyword_("languagesystem"):
                statements.append(self.parse_languagesystem_())
            elif self.is_cur_keyword_("lookup"):
                statements.append(self.parse_lookup_(vertical=False))
            elif self.is_cur_keyword_("markClass"):
                statements.append(self.parse_markClass_())
            elif self.is_cur_keyword_("feature"):
                statements.append(self.parse_feature_block_())
            elif self.is_cur_keyword_("table"):
                statements.append(self.parse_table_())
            elif self.is_cur_keyword_("valueRecordDef"):
                statements.append(
                    self.parse_valuerecord_definition_(vertical=False))
            elif self.cur_token_type_ is Lexer.NAME and self.cur_token_ in self.extensions:
                statements.append(self.extensions[self.cur_token_](self))
            elif self.cur_token_type_ is Lexer.SYMBOL and self.cur_token_ == ";":
                continue
            else:
                raise FeatureLibError(
                    "Expected feature, languagesystem, lookup, markClass, "
                    "table, or glyph class definition, got {} \"{}\"".format(self.cur_token_type_, self.cur_token_),
                    self.cur_token_location_)

        self.expect_symbol_("}")
        # self.expect_symbol_(";")  # can't have }; since tokens are space separated

    def parse_subblock_(self, block, vertical, stylisticset=False,
                            size_feature=None, cv_feature=None):
        self.expect_symbol_("{")
        for symtab in self.symbol_tables_:
            symtab.enter_scope()

        statements = block.statements
        while self.next_token_ != "}" or self.cur_comments_:
            self.advance_lexer_(comments=True)
            if self.cur_token_type_ is Lexer.COMMENT:
                statements.append(self.ast.Comment(
                    self.cur_token_, location=self.cur_token_location_))
            elif self.cur_token_type_ is Lexer.GLYPHCLASS:
                statements.append(self.parse_glyphclass_definition_())
            elif self.is_cur_keyword_("anchorDef"):
                statements.append(self.parse_anchordef_())
            elif self.is_cur_keyword_({"enum", "enumerate"}):
                statements.append(self.parse_enumerate_(vertical=vertical))
            elif self.is_cur_keyword_("feature"):
                statements.append(self.parse_feature_reference_())
            elif self.is_cur_keyword_("ignore"):
                statements.append(self.parse_ignore_())
            elif self.is_cur_keyword_("language"):
                statements.append(self.parse_language_())
            elif self.is_cur_keyword_("lookup"):
                statements.append(self.parse_lookup_(vertical))
            elif self.is_cur_keyword_("lookupflag"):
                statements.append(self.parse_lookupflag_())
            elif self.is_cur_keyword_("markClass"):
                statements.append(self.parse_markClass_())
            elif self.is_cur_keyword_({"pos", "position"}):
                statements.append(
                    self.parse_position_(enumerated=False, vertical=vertical))
            elif self.is_cur_keyword_("script"):
                statements.append(self.parse_script_())
            elif (self.is_cur_keyword_({"sub", "substitute",
                                        "rsub", "reversesub"})):
                statements.append(self.parse_substitute_())
            elif self.is_cur_keyword_("subtable"):
                statements.append(self.parse_subtable_())
            elif self.is_cur_keyword_("valueRecordDef"):
                statements.append(self.parse_valuerecord_definition_(vertical))
            elif stylisticset and self.is_cur_keyword_("featureNames"):
                statements.append(self.parse_featureNames_(stylisticset))
            elif cv_feature and self.is_cur_keyword_("cvParameters"):
                statements.append(self.parse_cvParameters_(cv_feature))
            elif size_feature and self.is_cur_keyword_("parameters"):
                statements.append(self.parse_size_parameters_())
            elif size_feature and self.is_cur_keyword_("sizemenuname"):
                statements.append(self.parse_size_menuname_())
            elif self.cur_token_type_ is Lexer.NAME and self.cur_token_ in self.extensions:
                statements.append(self.extensions[self.cur_token_](self))
            elif self.cur_token_ == ";":
                continue
            else:
                raise FeatureLibError(
                    "Expected glyph class definition or statement: got {} {}".format(self.cur_token_type_, self.cur_token_),
                    self.cur_token_location_)

        self.expect_symbol_("}")
        for symtab in self.symbol_tables_:
            symtab.exit_scope()

    def collect_block_(self):
        self.expect_symbol_("{")
        tokens = [(self.cur_token_type_, self.cur_token_)]
        count = 1
        while count > 0:
            self.advance_lexer_()
            if self.cur_token_ == "{":
                count += 1
            elif self.cur_token_ == "}":
                count -= 1
            tokens.append((self.cur_token_type_, self.cur_token_))
        return tokens

    def parseDoStatement_(self):
        location = self.cur_token_location_
        substatements = []
        while self.next_token_type_ is not Lexer.SYMBOL or self.next_token_ != "{":
            self.advance_lexer_()
            if self.is_cur_keyword_("for"):
                substatements.append(self.parseDoFor_())
            elif self.is_cur_keyword_("let"):
                substatements.append(self.parseDoLet_())
            elif self.is_cur_keyword_("if"):
                substatements.append(self.parseDoIf_())
            else:
                raise FeatureLibError("Unknown substatement type in do statement", self.cur_token_location_)
        block = self.collect_block_()
        lex = self.lexer_.lexers_[-1]
        res = self.ast.Block()
        keep = (self.next_token_type_, self.next_token_)
        block = [keep] + block + [keep]
        for s in self.DoIterateValues_(substatements):
            lex.scope = s
            lex.tokens = block[:]
            self.advance_lexer_()
            self.advance_lexer_()
            self.parse_subblock_(res, False)
        return res

    def DoIterateValues_(self, substatements):
        def updated(d, *a, **kw):
            d.update(*a, **kw)
            return d
        results = [{}]
        for s in substatements:
            results = [updated(x.copy(), {yk:yv}) for x in results for yk, yv in s.items(x) if yk is not None or yv is not None]
        for r in results:
            yield r

    def parseDoFor_(self):
        location = self.cur_token_location_
        self.advance_lexer_()
        if self.cur_token_type_ is Lexer.NAME:
            name = self.cur_token_
        else:
            raise FeatureLibError("Bad name in do for statement", location)
        self.expect_symbol_("=")
        glyphs = self.parse_glyphclass_(True)
        self.expect_symbol_(";")
        res = self.ast.DoForSubStatement(name, glyphs, location=location)
        return res

    def parseDoLet_(self):
        location = self.cur_token_location_
        self.advance_lexer_()
        if self.cur_token_type_ is Lexer.NAME:
            name = self.cur_token_
        else:
            raise FeatureLibError("Bad name in do let statement", location)
        if self.next_token_type_ != Lexer.SYMBOL or self.next_token_ != "=":
            raise FeatureLibError("Missing = in do let statement", self.next_token_location_)
        lex = self.lexer_.lexers_[-1]
        lex.scan_over_(Lexer.CHAR_WHITESPACE_)
        start = lex.pos_
        lex.scan_until_(";")
        expr = lex.text_[start:lex.pos_]
        self.advance_lexer_()
        self.expect_symbol_(";")
        return self.ast.DoLetSubStatement(name, expr, getattr(self, 'glyphs', None), location=location)

    def parseDoIf_(self):
        location = self.cur_token_location_
        start = self.next_token_location_
        lex = self.lexer_.lexers_[-1]
        lex.scan_until_(";")
        expr = lex.text_[start:lex.pos_]
        self.advance_lexer_()
        self.expect_symbol_(";")
        return self.ast.DoIfSubStatement(expr, location=location)

