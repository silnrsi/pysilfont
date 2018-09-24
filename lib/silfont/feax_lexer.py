from __future__ import unicode_literals
from fontTools.feaLib.lexer import IncludingLexer, Lexer
from fontTools.feaLib.error import FeatureLibError
import re, io

VARIABLE = "VARIABLE"

class feax_Lexer(Lexer):

    def __init__(self, *a):
        Lexer.__init__(self, *a)
        self.tokens = []

    def next_(self, recurse=False):
        if len(self.tokens) and not recurse:
            t = self.tokens.pop(0)
            if t[0] != VARIABLE:
                return (t[0], t[1], self.location_())
            return self.parse_variable(t[1])

        try:
            return Lexer.next_(self)
        except FeatureLibError as e:
            if u"Unexpected character" not in str(e):
                raise e

        location = self.location_()
        text = self.text_
        start = self.pos_
        cur_char = text[start]
        if cur_char == '$':
            self.pos_ += 1
            self.scan_over_(Lexer.CHAR_NAME_CONTINUATION_)
            varname = text[start+1:self.pos_]
            if len(varname) < 1 or len(varname) > 63:
                raise FeatureLibError("Bad variable name length", location)
            return (VARIABLE, varname, location)
        else:
            raise FeatureLibError("Unexpected character: %r" % cur_char, location)

    def pushback(self, token_type, token):
        self.tokens.insert(0, [token_type, token])
        
    def parse_variable(self, vname):
        t = self.scope.get(vname, '')
        stack = (self.text_, self.pos_)
        self.text_ = str(t) + " "
        self.pos_ = 0
        tok = self.next_(recurse=True)
        self.text_, self.pos_ = stack
        return (tok[0], tok[1], self.location_())

class feax_IncludingLexer(IncludingLexer):

    @staticmethod
    def make_lexer_(file_or_path):
        if hasattr(file_or_path, "read"):
            fileobj, closing = file_or_path, False
        else:
            filename, closing = file_or_path, True
            fileobj = io.open(filename, mode="r", encoding="utf-8")
        data = fileobj.read()
        filename = getattr(fileobj, "name", None)
        if closing:
            fileobj.close()
        return feax_Lexer(data, filename)

