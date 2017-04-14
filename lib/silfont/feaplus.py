from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser
from fontTools.feaLib.builder import Builder

class ast_BaseClass(ast.MarkClass) :
    def asFea(self, indent="") :
        return ""

class ast_BaseClassDefinition(ast.MarkClassDefinition) :
    def asFea(self, indent="") :
        return "# BaseClass @{}".format(self.markClass.name)

class ast_MarkBasePosStatement(ast.MarkBasePosStatement):
    def asFea(self, indent=""):
        if isinstance(self.base, ast.MarkClassName):
            res = ""
            for bcd in self.base.markClass.definitions:
                if res != "":
                    res += "\n{}".format(indent)
                res += "pos base {} {}".format(bcd.glyphs.asFea(), bcd.anchor.asFea())
                for m in self.marks:
                    res += " mark @{}".format(m.name)
                res += ";"
        else:
            res = "pos base {}".format(self.base.asFea())
            for a, m in self.marks:
                res += " {} mark @{}".format(a.asFea(), m.name)
            res += ";"
        return res

    def build(self, builder) :
        # do the right thing here
        pass

class feaplus_ast(object) :
    MarkBasePosStatement = ast_MarkBasePosStatement
    def __getattr__(self, name):
        return getattr(ast, name)

class feaplus_parser(Parser) :
    extensions = {
        'baseClass' : lambda s : s.parseBaseClass()
    }
    ast = feaplus_ast()

    def parse_position_base_(self, enumerated, vertical):
        location = self.cur_token_location_
        self.expect_keyword_("base")
        if enumerated:
            raise FeatureLibError(
                '"enumerate" is not allowed with '
                'mark-to-base attachment positioning',
                location)
        base = self.parse_glyphclass_(accept_glyphname=True)
        if self.next_token_ == "<":
            marks = self.parse_anchor_marks_()
        else:
            marks = []
            while self.next_token_ == "mark":
                self.expect_keyword_("mark")
                m = self.expect_markClass_reference_()
                marks.append(m)
        self.expect_symbol_(";")
        return self.ast.MarkBasePosStatement(location, base, marks)

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
            baseClass = ast_BaseClass(name)
            self.doc_.baseClasses[name] = baseClass
            self.glyphclasses_.define(name, baseClass)
        bcdef = ast_BaseClassDefinition(location, baseClass, anchor, glyphs)
        baseClass.addDefinition(bcdef)
        return bcdef
