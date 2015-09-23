#    Copyright 2012, SIL International
#    All rights reserved.
#
#    This library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 2.1 of License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should also have received a copy of the GNU Lesser General Public
#    License along with this library in the file named "LICENSE".
#    If not, write to the Free Software Foundation, 51 Franklin Street,
#    suite 500, Boston, MA 02110-1335, USA or visit their web page on the 
#    internet at http://www.fsf.org/licenses/lgpl.html.

import re, traceback, logging
from fontTools.ttLib.tables import otTables

def compress_strings(strings) :
    '''If we replace one column in the string with different lists, can we reduce the number
       of strings? Each string is a tuple of the string and a single value that will be put into
       a class as well when list compression occurs'''
    maxlen = max(map(lambda x: len(x[0]), strings))
    scores = []
    for r in range(maxlen) :
        allchars = {}
        count = 0
        for s in strings :
            if r >= len(s[0]) : continue
            c = tuple(s[0][0:r] + (s[0][r+1:] if r < len(s[0]) - 1 else []))
            if c in allchars :
                allchars[c] += 1
            else :
                allchars[c] = 0
            count += 1
        scores.append((max(allchars.values()), len(allchars), count))
    best = maxlen
    bestr = 0
    for r in range(maxlen) :
        score = maxlen - (scores[r][2] - scores[r][1])
        if score < best :
            best = score
            bestr = r
    numstrings = len(strings)
    i = 0
    allchars = {}
    while i < len(strings) :
        s = strings[i][0]
        if bestr >= len(s) :
            i += 1
            continue
        c = tuple(s[0:bestr] + (s[bestr+1:] if bestr < len(s) - 1 else []))
        if c in allchars :
            allchars[c][1].append(s[bestr])
            allchars[c][2].append(strings[i][1])
            strings.pop(i)
        else :
            allchars[c] = [i, [s[bestr]], [strings[i][1]]]
            i += 1
    for v in allchars.values() :
        if len(set(v[1])) != 1 :    # if all values in the list identical, don't output list
            strings[v[0]][0][bestr] = v[1]
        if len(v[2]) > 1 :          # don't need a list if length 1
            strings[v[0]][1] = v[2]
    return strings

def make_rule(left, right = None, before = None, after = None) :
    res = " ".join(map(lambda x: x or "_", left))
    if right :
        res += " > " + " ".join(map(lambda x: x or "_", right))
    if before or after :
        res += " / "
        if before : res += " ".join(map(lambda x: x or 'ANY', before))
        res += " " + "_ " * len(left) + " "
        if after : res += " ".join(map(lambda x: x or 'ANY', after))
    res += ";"
    return res

def add_class_classes(font, name, ctable) :
    vals = {}
    for k, v in ctable.classDefs.items() :
        if v not in vals : vals[v] = []
        vals[v].append(k)
    numk = max(vals.keys())
    res = [None] * (numk + 1)
    for k, v in vals.items() :
        if len(v) > 1 :
            res[k] = font.alias(name+"{}".format(k))
            font.addClass(res[k], map(font.glyph, v))
        else :
            res[k] = font.glyph(v[0]).GDLName()
    return res

vrgdlmap = {
    'XPlacement' : 'shift.x',
    'YPlacement' : 'shift.y',
    'XAdvance' : 'advance'
}
def valuerectogdl(vr) :
    res = "{"
    for k, v in vrgdlmap.items() :
        if hasattr(vr, k) :
            res += "{}={}; ".format(v, getattr(vr, k))
    res = res[:-1] + "}"
    if len(res) == 1 : return ""
    return res

def _add_method(*clazzes):
    """Returns a decorator function that adds a new method to one or
    more classes."""
    def wrapper(method):
        for c in clazzes:
            assert c.__name__ != 'DefaultTable', \
                    'Oops, table class not found.'
            assert not hasattr(c, method.__name__), \
                    "Oops, class '%s' has method '%s'." % (c.__name__,
                                                           method.__name__)
            setattr(c, method.__name__, method)
        return None
    return wrapper

@_add_method(otTables.Lookup)
def process(self, font, index) :
    for i, s in enumerate(self.SubTable) :
        if hasattr(s, 'process') :
            s.process(font, index + "_{}".format(i))
        else :
            logging.warning("No processing of {} {}_{}".format(str(s), index, i))

@_add_method(otTables.LookupList)
def process(self, font) :
    for i, s in enumerate(self.Lookup) :
        s.process(font, str(i))

@_add_method(otTables.ExtensionSubst, otTables.ExtensionPos)
def process(self, font, index) :
    x = self.ExtSubTable
    if hasattr(x, 'process') :
        x.process(font, index)
    else :
        logging.warning("No processing of {} {}".format(str(x), index))

@_add_method(otTables.SingleSubst)
def process(self, font, index) :
    cname = "cot_s{}".format(index)
    if not len(font.alias(cname)) : return
    lists = zip(*self.mapping.items())
    font.addClass(font.alias(cname+"l"), map(font.glyph, lists[0]))
    font.addClass(font.alias(cname+"r"), map(font.glyph, lists[1]))

@_add_method(otTables.MultipleSubst)
def process(self, font, index) :
    cname = "cot_m{}".format(index)
    if not len(font.alias(cname)) : return
    nums = len(self.Coverage.glyphs)
    strings = []
    for i in range(nums) :
        strings.append([self.Sequence[i].Substitute, self.Coverage.glyphs[i]])
    res = compress_strings(strings)
    count = 0
    rules = []
    for r in res :
        if hasattr(r[1], '__iter__') :
            lname = font.alias(cname+"l{}".format(count))
            font.addClass(lname, map(font.glyph, r[1]))
            rule = lname
        else :
            rule = font.glyph(r[1]).GDLName()
        rule += " _" * (len(r[0]) - 1) + " >"
        for c in r[0] :
            if hasattr(c, '__iter__') :
                rname = font.alias(cname+"r{}".format(count))
                font.addClass(rname, map(font.glyph, c))
                rule += " " + rname
                count += 1
            else :
                rule += " " + font.glyph(c).GDLName()
        rule += ';'
        rules.append(rule)
    font.addRules(rules, index)

@_add_method(otTables.LigatureSubst)
def process(self, font, index) :
    cname = "cot_l{}".format(index)
    if not len(font.alias(cname)) : return
    strings = []
    for lg, ls in self.ligatures.items() :
        for l in ls :
            strings.append([[lg] + l.Component, l.LigGlyph])
    res = compress_strings(strings)
    count = 0
    rules = []
    for r in res :
        rule = ""
        besti = 0
        for i, c in enumerate(r[0]) :
            if hasattr(c, '__iter__') :
                lname = font.alias(cname+"l{}".format(count))
                font.addClass(lname, map(font.glyph, c))
                rule += lname + " "
                besti = i
            else :
                rule += font.glyph(c).GDLName() + " "
        rule += "> " + "_ " * besti
        if hasattr(r[1], '__iter__') :
            rname = font.alias(cname+"r{}".format(count))
            font.addClass(rname, map(font.glyph, r[1]))
            rule += rname
            count += 1
        else :
            rule += font.glyph(r[1]).GDLName()
        rule += " _" * (len(r[0]) - 1 - besti) + ";"
        rules.append(rule)
    font.addRules(rules, index)

@_add_method(otTables.ChainContextSubst)
def process(self, font, index) :

    def procsubst(rule, action) :
        for s in rule.SubstLookupRecord :
            action[s.SequenceIndex] += "/*{}*/".format(s.LookupListIndex)
    def procCover(cs, name) :
        res = []
        for i, c in enumerate(cs) :
            if len(c.glyphs) > 1 :
                n = font.alias(name+"{}".format(i))
                font.addClass(n, map(font.glyph, c.glyphs))
                res.append(n)
            else :
                res.append(font.glyph(c.glyphs[0]).GDLName())
        return res

    cname = "cot_c{}".format(index)
    if not len(font.alias(cname)) : return
    rules = []
    if self.Format == 1 :
        for i in range(len(self.ChainSubRuleSet)) :
            for r in self.ChainSubRuleSet[i].ChainSubRule :
                action = [self.Coverage.glyphs[i]] + r.Input
                procsubst(r, action)
                rules.append(make_rule(action, None, r.Backtrack, r.LookAhead))
    elif self.Format == 2 :
        ilist = add_class_classes(font, cname+"i", self.InputClassDef)
        if self.BacktrackClassDef :
            blist = add_class_classes(font, cname+"b", self.BacktrackClassDef)
        if self.LookAheadClassDef :
            alist = add_class_classes(font, cname+"a", self.LookAheadClassDef)
        for i, s in enumerate(self.ChainSubClassSet) :
            if s is None : continue
            for r in s.ChainSubClassRule :
                action = map(lambda x:ilist[x], [i]+r.Input)
                procsubst(r, action)
                rules.append(make_rule(action, None,
                                        map(lambda x:blist[x], r.Backtrack or []),
                                        map(lambda x:alist[x], r.LookAhead or [])))
    elif self.Format == 3 :
        backs = procCover(self.BacktrackCoverage, cname+"b")
        aheads = procCover(self.LookAheadCoverage, cname+"a")
        actions = procCover(self.InputCoverage, cname+"i")
        procsubst(self, actions)
        rules.append(make_rule(actions, None, backs, aheads))
    font.addRules(rules, index)

@_add_method(otTables.SinglePos)
def process(self, font, index) :
    cname = "cot_p{}".format(index)
    if self.Format == 1 :
        font.addClass(font.alias(cname), map(font.glyph, self.Coverage.glyphs))
        rule = cname + " " + valuerectogdl(self.Value)
        font.addPosRules([rule], index)
    elif self.Format == 2 :
        rules = []
        for i, g in enumerage(map(font.glyph, self.Coverage.glyphs)) :
            rule = font.glyph(g).GDLName()
            rule += " " + valuerectogdl(self.Value[i])
            rules.append(rule)
        font.addPosRules(rules, index)

@_add_method(otTables.PairPos)
def process(self, font, index) :
    pass

@_add_method(otTables.CursivePos)
def process(self, font, index) :
    apname = "P{}".format(index)
    if not len(font.alias(apname)) : return
    if self.Format == 1 :
        mark_names = self.Coverage.glyphs
        for i, g in enumerate(map(font.glyph, mark_names)) :
            rec = self.EntryExitRecord[i]
            if rec.EntryAnchor is not None :
                g.setAnchor(font.alias(apname+"_{}M".format(rec.EntryAnchor)),
                            rec.EntryAnchor.XCoordinate, rec.EntryAnchor.YCoordinate)
            if rec.ExitAnchor is not None :
                g.setAnchor(font.alias(apname+"_{}S".format(rec.ExitAnchor)),
                            rec.ExitAnchor.XCoordinate, rec.ExitAnchor.YCoordinate)

@_add_method(otTables.MarkBasePos)
def process(self, font, index) :
    apname = "P{}".format(index)
    if not len(font.alias(apname)) : return
    if self.Format == 1 :
        mark_names = self.MarkCoverage.glyphs
        for i, g in enumerate(map(font.glyph, mark_names)) :
            rec = self.MarkArray.MarkRecord[i]
            g.setAnchor(font.alias(apname+"_{}M".format(rec.Class)),
                        rec.MarkAnchor.XCoordinate, rec.MarkAnchor.YCoordinate) 
        base_names = self.BaseCoverage.glyphs
        for i, g in enumerate(map(font.glyph, base_names)) :
            for j,b in enumerate(self.BaseArray.BaseRecord[i].BaseAnchor) :
                if b : g.setAnchor(font.alias(apname+"_{}S".format(j)),
                                    b.XCoordinate, b.YCoordinate)

@_add_method(otTables.MarkMarkPos)
def process(self, font, index) :
    apname = "P{}".format(index)
    if not len(font.alias(apname)) : return
    if self.Format == 1 :
        mark_names = self.Mark1Coverage.glyphs
        for i, g in enumerate(map(font.glyph, mark_names)) :
            rec = self.Mark1Array.MarkRecord[i]
            g.setAnchor(font.alias(apname+"_{}M".format(rec.Class)),
                        rec.MarkAnchor.XCoordinate, rec.MarkAnchor.YCoordinate) 
        base_names = self.Mark2Coverage.glyphs
        for i, g in enumerate(map(font.glyph, base_names)) :
            for j,b in enumerate(self.Mark2Array.Mark2Record[i].Mark2Anchor) :
                if b : g.setAnchor(font.alias(apname+"_{}S".format(j)),
                                    b.XCoordinate, b.YCoordinate)

@_add_method(otTables.ContextSubst)
def process(self, font, index) :

    def procsubst(rule, action) :
        for s in rule.SubstLookupRecord :
            action[s.SequenceIndex] += "/*{}*/".format(s.LookupListIndex)
    def procCover(cs, name) :
        res = []
        for i, c in enumerate(cs) :
            if len(c.glyphs) > 1 :
                n = font.alias(name+"{}".format(i))
                font.addClass(n, map(font.glyph, c.glyphs))
                res.append(n)
            else :
                res.append(font.glyph(c.glyphs[0]).GDLName())
        return res

    cname = "cot_cs{}".format(index)
    if not len(font.alias(cname)) : return
    rules = []
    if self.Format == 1 :
        for i in range(len(self.SubRuleSet)) :
            for r in self.SubRuleSet[i].SubRule :
                action = [self.Coverage.glyphs[i]] + r.Input
                procsubst(r, action)
                rules.append(make_rule(action, None, None, None))
    elif self.Format == 2 :
        ilist = add_class_classes(font, cname+"i", self.ClassDef)
        for i, s in enumerate(self.SubClassSet) :
            if s is None : continue
            for r in s.SubClassRule :
                action = map(lambda x:ilist[x], [i]+r.Class)
                procsubst(r, action)
                rules.append(make_rule(action, None, None, None))
    elif self.Format == 3 :
        actions = procCover(self.Coverage, cname+"i")
        procsubst(self, actions)
        rules.append(make_rule(actions, None, None, None))
    font.addRules(rules, index)

@_add_method(otTables.ContextPos)
def process(self, font, index) :

    def procsubst(rule, action) :
        for s in rule.PosLookupRecord :
            action[s.SequenceIndex] += "/*{}*/".format(s.LookupListIndex)
    def procCover(cs, name) :
        res = []
        for i, c in enumerate(cs) :
            if len(c.glyphs) > 1 :
                n = font.alias(name+"{}".format(i))
                font.addClass(n, map(font.glyph, c.glyphs))
                res.append(n)
            else :
                res.append(font.glyph(c.glyphs[0]).GDLName())
        return res

    cname = "cot_cp{}".format(index)
    if not len(font.alias(cname)) : return
    rules = []
    if self.Format == 1 :
        for i in range(len(self.PosRuleSet)) :
            for r in self.PosRuleSet[i] :
                action = [self.Coverage.glyphs[i]] + r.Input
                procsubst(r, action)
                rules.append(make_rule(action, None, None, None))
    elif self.Format == 2 :
        ilist = add_class_classes(font, cname+"i", self.ClassDef)
        for i, s in enumerate(self.PosClassSet) :
            if s is None : continue
            for r in s.PosClassRule :
                action = map(lambda x:ilist[x], [i]+r.Class)
                procsubst(r, action)
                rules.append(make_rule(action, None, None, None))
    elif self.Format == 3 :
        actions = procCover(self.Coverage, cname+"i")
        procsubst(self, actions)
        rules.append(make_rule(actions, None, None, None))
    font.addPosRules(rules, index)

@_add_method(otTables.ChainContextPos)
def process(self, font, index) :

    def procsubst(rule, action) :
        for s in rule.PosLookupRecord :
            action[s.SequenceIndex] += "/*{}*/".format(s.LookupListIndex)
    def procCover(cs, name) :
        res = []
        for i, c in enumerate(cs) :
            if len(c.glyphs) > 1 :
                n = font.alias(name+"{}".format(i))
                font.addClass(n, map(font.glyph, c.glyphs))
                res.append(n)
            else :
                res.append(font.glyph(c.glyphs[0]).GDLName())
        return res

    cname = "cot_c{}".format(index)
    if not len(font.alias(cname)) : return
    rules = []
    if self.Format == 1 :
        for i in range(len(self.ChainPosRuleSet)) :
            for r in self.ChainPosRuleSet[i].ChainPosRule :
                action = [self.Coverage.glyphs[i]] + r.Input
                procsubst(r, action)
                rules.append(make_rule(action, None, r.Backtrack, r.LookAhead))
    elif self.Format == 2 :
        ilist = add_class_classes(font, cname+"i", self.InputClassDef)
        if self.BacktrackClassDef :
            blist = add_class_classes(font, cname+"b", self.BacktrackClassDef)
        if self.LookAheadClassDef :
            alist = add_class_classes(font, cname+"a", self.LookAheadClassDef)
        for i, s in enumerate(self.ChainPosClassSet) :
            if s is None : continue
            for r in s.ChainPosClassRule :
                action = map(lambda x:ilist[x], [i]+r.Input)
                procsubst(r, action)
                rules.append(make_rule(action, None,
                                        map(lambda x:blist[x], r.Backtrack or []),
                                        map(lambda x:alist[x], r.LookAhead or [])))
    elif self.Format == 3 :
        backs = procCover(self.BacktrackCoverage, cname+"b")
        aheads = procCover(self.LookAheadCoverage, cname+"a")
        actions = procCover(self.InputCoverage, cname+"i")
        procsubst(self, actions)
        rules.append(make_rule(actions, None, backs, aheads))
    font.addPosRules(rules, index)

