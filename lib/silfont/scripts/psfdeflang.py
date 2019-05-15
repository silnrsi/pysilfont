#!/usr/bin/env python
from __future__ import unicode_literals
__doc__ = '''Switch default language in a font'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.core import execute

argspec = [
    ('ifont',{'help': 'Input TTF'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output TTF','nargs': '?' }, {'type': 'outfont'}),
    ('-L','--lang', {'help': 'Language to switch to'}, {})
]

def long2tag(x):
    res = []
    while x:
        res.append(chr(x & 0xFF))
        x >>= 8
    return "".join(reversed(res))

def doit(args):
    infont = args.ifont
    ltag = args.lang.lower()
    if 'Sill' in infont and 'Feat' in infont:
        if ltag in infont['Sill'].langs:
            changes = dict((long2tag(x[0]), x[1]) for x in infont['Sill'].langs[ltag])
            for g, f in infont['Feat'].features.items():
                if g in changes:
                    f.default = changes[g]
    otltag = ltag + (" " * (4 - len(ltag)))
    for k in ('GSUB', 'GPOS'):
        try:
            t = infont[k].table
        except KeyError:
            continue
        for srec in t.ScriptList.ScriptRecord:
            for lrec in srec.Script.LangSysRecord:
                if lrec.LangSysTag.lower() == otltag:
                    srec.Script.DefaultLangSys = lrec.LangSys
    return infont

def cmd() : execute('FT', doit, argspec)
if __name__ == "__main__" : cmd()

