#!/usr/bin/env python
'Add empty Opentype tables to ttf font'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'

from fontTools import ttLib
from fontTools.ttLib.tables import otTables
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('infont', help='Input font file')
parser.add_argument('outfont', help='Output font file')
parser.add_argument('-s','--script',default='DFLT', help='Script tag to generate [DFLT]')
parser.add_argument('-t','--type',default='both', help='Table to create: gpos, gsub, [both]')
args = parser.parse_args()

inf = ttLib.TTFont(args.infont)
for tag in ('GSUB', 'GPOS') :
    if tag.lower() == args.type or args.type == 'both' :
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
        inf[tag] = table
inf.save(args.outfont)
