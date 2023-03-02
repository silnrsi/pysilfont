#!/usr/bin/env python
__doc__ = '''Merge lookup and feature aliases into TypeTuner feature file'''
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.core import execute
from xml.etree import ElementTree as ET
from fontTools import ttLib
import csv
import struct

argspec = [
    ('input', {'help': 'Input TypeTuner feature file'}, {'type': 'infile'}),
    ('output', {'help': 'Output TypeTuner feature file'}, {}),
    ('-m','--mapping', {'help': 'Input csv mapping file'}, {'type': 'incsv'}),
    ('-f','--ttf', {'help': 'Compiled TTF file'}, {}),
    ('-l','--log',{'help': 'Optional log file'}, {'type': 'outfile', 'def': '_tuneraliases.log', 'optlog': True}),
    ]

def doit(args) :
    logger = args.logger

    if args.mapping is None and args.ttf is None:
        logger.log("One or both of -m and -f must be provided", "S")
    featdoc = ET.parse(args.input)
    root = featdoc.getroot()
    if root.tag != 'all_features':
        logger.log("Invalid TypeTuner feature file: missing root element", "S")

    # Whitespace to add after each new alias:
    tail = '\n\t\t'

    # Find or add alliaes element
    aliases = root.find('aliases')
    if aliases is None:
        aliases = ET.SubElement(root,'aliases')
        aliases.tail = '\n'

    added = set()
    duplicates = set()
    def setalias(name, value):
        # detect duplicate names in input
        if name in added:
            duplicates.add(name)
        else:
            added.add(name)
        # modify existing or add new alias
        alias = aliases.find('alias[@name="{}"]'.format(name))
        if alias is None:
            alias = ET.SubElement(aliases, 'alias', {'name': name, 'value': value})
            alias.tail = tail
        else:
            alias.set('value', value)

    # Process mapping file if present:
    if args.mapping:
        # Mapping file is assumed to come from psfbuildfea, and should look like:
        #      lookupname,table,index
        # e.g. DigitAlternates,GSUB,51
        for (name,table,value) in args.mapping:
            setalias(name, value)

    # Process the ttf file if present
    if args.ttf:
        # Generate aliases for features.
        # In this code featureID means the key used in FontUtils for finding the feature, e.g., "calt _2"
        def dotable(t):     # Common routine for GPOS and GSUB
            currtag = None
            currtagindex = None
            flist = []     # list, in order, of (featureTag, featureID), per Font::TTF
            for i in range(0,t.FeatureList.FeatureCount):
                newtag = str(t.FeatureList.FeatureRecord[i].FeatureTag)
                if currtag is None or currtag != newtag:
                    flist.append((newtag, newtag))
                    currtag = newtag
                    currtagindex = 0
                else:
                    flist.append( (currtag, '{} _{}'.format(currtag, currtagindex)))
                    currtagindex += 1
            fslList = {}     # dictionary keyed by feature_script_lang values returning featureID
            for s in t.ScriptList.ScriptRecord:
                currtag = str(s.ScriptTag)
                # At present only looking at the dflt lang entries
                for findex in s.Script.DefaultLangSys.FeatureIndex:
                    fslList['{}_{}_dflt'.format(flist[findex][0],currtag)] = flist[findex][1]
            # Now that we have them all, add them in sorted order.
            for name, value in sorted(fslList.items()):
                setalias(name,value)

        # Open the TTF for processing
        try:
            f = ttLib.TTFont(args.ttf)
        except Exception as e:
            logger.log("Couldn't open font '{}' for reading : {}".format(args.ttf, str(e)),"S")
        # Grab features from GSUB and GPOS
        for tag in ('GSUB', 'GPOS'):
            try:
                dotable(f[tag].table)
            except Exception as e:
                logger.log("Failed to process {} table: {}".format(tag, str(e)), "W")
        # Grab features from Graphite:
        try:
            for tag in sorted(f['Feat'].features.keys()):
                if tag == '1':
                    continue
                name = 'gr_' + tag
                value = str(struct.unpack('>L', tag.encode())[0])
                setalias(name,value)
        except Exception as e:
            logger.log("Failed to process Feat table: {}".format(str(e)), "W")

    if len(duplicates):
        logger.log("The following aliases defined more than once in input: {}".format(", ".join(sorted(duplicates))), "S")

    # Success. Write the result
    featdoc.write(args.output, encoding='UTF-8', xml_declaration=True)

def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
