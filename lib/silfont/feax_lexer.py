from fontTools.feaLib.lexer import IncludingLexer, Lexer
from fontTools.feaLib.error import FeatureLibError
import re, io

VARIABLE = "VARIABLE"

class feax_Lexer(Lexer):

    def __init__(self, *a):
        Lexer.__init__(self, *a)
        self.tokens_ = None
        self.stack_ = []
        self.empty_ = False

    def next_(self, recurse=False):
        while (not self.empty_):
            if self.tokens_ is not None:
                res = self.tokens_.pop(0)
                if not len(self.tokens_):
                    self.popstack()
                if res[0] != VARIABLE:
                    return (res[0], res[1], self.location_())
                return self.parse_variable(res[1])

            try:
                res = Lexer.next_(self)
            except IndexError as e:
                self.popstack()
                continue
            except StopIteration as e:
                self.popstack()
                continue
            except FeatureLibError as e:
                if u"Unexpected character" not in str(e):
                    raise e

                # only executes if exception occurred
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
                    res = (VARIABLE, varname, location)
                else:
                    raise FeatureLibError("Unexpected character: %r" % cur_char, location)
            return res
        raise StopIteration

    def __repr__(self):
        if self.tokens_ is not None:
            return str(self.tokens_)
        else:
            return str((self.text_[self.pos_:self.pos_+20], self.pos_, self.text_length_))

    def popstack(self):
        if len(self.stack_) == 0:
            self.empty_ = True
            return
        t = self.stack_.pop()
        if t[0] == 'tokens':
            self.tokens_ = t[1]
        else:
            self.text_, self.pos_, self.text_length_ = t[1]
            self.tokens_ = None

    def pushstack(self, v):
        if self.tokens_ is None:
            self.stack_.append(('text', (self.text_, self.pos_, self.text_length_)))
        else:
            self.stack_.append(('tokens', self.tokens_))
        self.stack_.append(v)
        self.popstack()

    def pushback(self, token_type, token):
        if self.tokens_ is not None:
            self.tokens_.append((token_type, token))
        else:
            self.pushstack(('tokens', [(token_type, token)]))
        
    def parse_variable(self, vname):
        t = str(self.scope.get(vname, ''))
        if t != '':
            self.pushstack(['text', (t + " ", 0, len(t)+1)])
        return self.next_()

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

