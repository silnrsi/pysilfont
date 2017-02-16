#!/usr/bin/env python
'Add empty Opentype tables to ttf font'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from silfont.core import execute
from fontTools import ttLib
from fontTools.ttLib.tables import otTables

argspec = [
    ('ifont',{'help': 'Input font file'}, {'type': 'infont'}),
    ('ofont',{'help': 'Output font file','nargs': '?' }, {'type': 'outfont'}),
    ('-l','--log',{'help': 'Log file'}, {'type': 'outfile', 'def': '_conv.log'}),
    ('-s','--script',{'help': 'Script tag to generate [DFLT]', 'default': 'DFLT', }, {}),
    ('-t','--type',{'help': 'Table to create: gpos, gsub, [both]', 'default': 'both', }, {})    ]

def doit(args) :
    font = args.ifont
    args.type = args.type.upper()

    for tag in ('GSUB', 'GPOS') :
        if tag == args.type or args.type == 'BOTH' :
            table = ttLib.getTableClass(tag)()
            t = getattr(otTables, tag, None)()
            t.Version = 1.0
            t.ScriptList = otTables.ScriptList()
            t.ScriptList.ScriptRecord = []
            t.FeatureList = otTables.FeatureList()
            t.FeatureList.FeatureRecord = []
            t.LookupList = otTables.LookupList()
            t.LookupList.Lookup = []
            srec = otTables.ScriptRecord()
            srec.ScriptTag = args.script
            srec.Script = otTables.Script()
            srec.Script.DefaultLangSys = None
            srec.Script.LangSysRecord = []
            t.ScriptList.ScriptRecord.append(srec)
            t.ScriptList.ScriptCount = 1
            t.FeatureList.FeatureCount = 0
            t.LookupList.LookupCount = 0
            table.table = t
            font[tag] = table

    return font

def cmd() : execute("FT",doit, argspec)
if __name__ == "__main__": cmd()
