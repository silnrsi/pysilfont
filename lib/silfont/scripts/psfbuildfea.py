#!/usr/bin/python3
from __future__ import unicode_literals
__doc__ = 'Build features.fea file into a ttf font'
# TODO: add conditional compilation, compare to fea, compile to ttf
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2017 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Martin Hosken'

from fontTools.feaLib.builder import Builder
from fontTools import configLogger
from fontTools.ttLib import TTFont

from silfont.core import execute

class MyBuilder(Builder):

    def __init__(self, font, featurefile, lateSortLookups = False):
        super(MyBuilder, self).__init__(font, featurefile)
        self.lateSortLookups = lateSortLookups

    def buildLookups_(self, tag):
        assert tag in ('GPOS', 'GSUB'), tag
        countFeatureLookups = 0
        for lookup in self.lookups_:
            lookup.lookup_index = None
            if lookup.table == tag and getattr(lookup, '_feature', "") != "":
                countFeatureLookups += 1
        lookups = []
        latelookups = []
        for lookup in self.lookups_:
            if lookup.table != tag:
                continue
            if self.lateSortLookups and getattr(lookup, '_feature', "") == "":
                lookup.lookup_index = countFeatureLookups + len(latelookups)
                latelookups.append(lookup)
            else:
                lookup.lookup_index = len(lookups)
                lookups.append(lookup)
            lookup.map_index = lookup.lookup_index
        return [l.build() for l in lookups + latelookups]

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
]

def doit(args) :
    levels = ["WARNING", "INFO", "DEBUG"]
    configLogger(level=levels[min(len(levels) - 1, args.verbose)])

    font = TTFont(args.input_font)
    builder = MyBuilder(font, args.input_fea, lateSortLookups = args.end)
    builder.build()
    if args.lookupmap:
        with open(args.lookupmap, "w") as outf:
            for n, l in sorted(builder.named_lookups_.items()):
                if l is not None:
                    outf.write("{},{},{}\n".format(n, l.table, l.map_index))
    font.save(args.output)

def cmd(): execute(None, doit, argspec)
if __name__ == '__main__': cmd()
