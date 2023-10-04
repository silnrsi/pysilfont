#!/usr/bin/env python3
__doc__ = 'Build features.fea file into a ttf font'
# TODO: add conditional compilation, compare to fea, compile to ttf
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from fontTools.feaLib.builder import Builder
from fontTools import configLogger
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import lookupTypes
from fontTools.feaLib.lookupDebugInfo import LookupDebugInfo

from silfont.core import execute

class MyBuilder(Builder):

    def __init__(self, font, featurefile, lateSortLookups=False, fronts=None):
        super(MyBuilder, self).__init__(font, featurefile)
        self.lateSortLookups = lateSortLookups
        self.fronts = fronts if fronts is not None else []

    def buildLookups_(self, tag):
        assert tag in ('GPOS', 'GSUB'), tag
        countFeatureLookups = 0
        fronts = set([l for k, l in self.named_lookups_.items() if k in self.fronts])
        for bldr in self.lookups_:
            bldr.lookup_index = None
            if bldr.table == tag and getattr(bldr, '_feature', "") != "":
                countFeatureLookups += 1
        lookups = []
        latelookups = []
        for bldr in self.lookups_:
            if bldr.table != tag:
                continue
            if self.lateSortLookups and getattr(bldr, '_feature', "") == "":
                if bldr in fronts:
                    latelookups.insert(0, bldr)
                else:
                    latelookups.append(bldr)
            else:
                bldr.lookup_index = len(lookups)
                lookups.append(bldr)
                bldr.map_index = bldr.lookup_index
        numl = len(lookups)
        for i, l in enumerate(latelookups):
            l.lookup_index = numl + i
            l.map_index = l.lookup_index
        for l in lookups + latelookups:
            self.lookup_locations[tag][str(l.lookup_index)] = LookupDebugInfo(
                    location=str(l.location),
                    name=self.get_lookup_name_(l),
                    feature=None)
        return [b.build() for b in lookups + latelookups]

    def add_lookup_to_feature_(self, lookup, feature_name):
        super(MyBuilder, self).add_lookup_to_feature_(lookup, feature_name)
        lookup._feature = feature_name


#TODO: provide more argument info
argspec = [
    ('input_fea', {'help': 'Input fea file'}, {}),
    ('input_font', {'help': 'Input font file'}, {}),
    ('-o', '--output', {'help': 'Output font file'}, {}),
    ('-v', '--verbose', {'help': 'Repeat to increase verbosity', 'action': 'count', 'default': 0}, {}),
    ('-m', '--lookupmap', {'help': 'File into which place lookup map'}, {}),
    ('-l','--log',{'help': 'Optional log file'}, {'type': 'outfile', 'def': '_buildfea.log', 'optlog': True}),
    ('-e','--end',{'help': 'Push lookups not in features to the end', 'action': 'store_true'}, {}),
    ('-F','--front',{'help': 'Pull named lookups to the front of unnamed list', 'action': 'append'}, {}),
]

def doit(args) :
    levels = ["WARNING", "INFO", "DEBUG"]
    configLogger(level=levels[min(len(levels) - 1, args.verbose)])

    font = TTFont(args.input_font)
    builder = MyBuilder(font, args.input_fea, lateSortLookups=args.end, fronts=args.front)
    builder.build()
    if args.lookupmap:
        with open(args.lookupmap, "w") as outf:
            for n, l in sorted(builder.named_lookups_.items()):
                if l is not None:
                    outf.write("{},{},{}\n".format(n, l.table, l.map_index))
    font.save(args.output)

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
