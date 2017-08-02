from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser
from fontTools.feaLib.builder import Builder

class ast_BaseClass(ast.MarkClass) :
    def asFea(self, indent="") :
        # should not be used since BaseClass is flattened to BaseClassDefinitions
        # in ast_MarkBasePosStatement.asFea and not output directly
        return ""

class ast_BaseClassDefinition(ast.MarkClassDefinition) :
    def asFea(self, indent="") :
        # like base class asFea
        return "{}baseClass {} {} @{};".format(indent, self.glyphs.asFea(),
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

class feaplus_ast(object) :
    MarkBasePosStatement = ast_MarkBasePosStatement
    BaseClass = ast_BaseClass
    BaseClassDefinition = ast_BaseClassDefinition

    def __getattr__(self, name):
        return getattr(ast, name)

class feaplus_parser(Parser) :
    extensions = {
        'baseClass' : lambda s : s.parseBaseClass()
    }
    ast = feaplus_ast()

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
