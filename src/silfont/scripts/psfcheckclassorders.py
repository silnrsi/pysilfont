#!/usr/bin/env python3
'''verify classes defined in xml have correct ordering where needed

Looks for comment lines in the classes.xml file that match the string:
  *NEXT n CLASSES MUST MATCH*
where n is the number of upcoming class definitions that must result in the
same glyph alignment when glyph names are sorted by TTF order (as described
in the glyph_data.csv file).
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019-2025, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

import re
import types
from xml.etree import ElementTree as ET
from silfont.core import execute

argspec = [
    ('classes', {'help': 'class definition in XML format', 'nargs': '?', 'default': 'classes.xml'}, {'type': 'infile'}),
    ('glyphdata', {'help': 'Glyph info csv file', 'nargs': '?', 'default': 'glyph_data.csv'}, {'type': 'incsv'}),
    ('--gname', {'help': 'Column header for glyph name', 'default': 'glyph_name'}, {}),
    ('--sort', {'help': 'Column header(s) for sort order', 'default': 'sort_final'}, {}),
]

# Dictionary of glyphName : sortValue
sorts = dict()

# Keep track of glyphs mentioned in classes but not in glyph_data.csv
missingGlyphs = set()

def doit(args):
    logger = args.logger

    # Read input csv to get glyph sort order
    incsv = args.glyphdata
    fl = incsv.firstline
    if fl is None: logger.log("Empty input file", "S")
    if args.gname in fl:
        glyphnpos = fl.index(args.gname)
    else:
        logger.log("No" + args.gname + "field in csv headers", "S")
    if args.sort in fl:
        sortpos = fl.index(args.sort)
    else:
        logger.log('No "' + args.sort + '" heading in csv headers"', "S")
    next(incsv.reader, None)  # Skip first line with containing headers
    for line in incsv:
        glyphn = line[glyphnpos]
        if len(glyphn) == 0:
            continue	# No need to include cases where name is blank
        sorts[glyphn] = float(line[sortpos])

    # RegEx we are looking for in comments
    matchCountRE = re.compile(r"\*NEXT ([1-9]\d*) CLASSES MUST MATCH\*")

    # parse classes.xml but include comments
    class MyTreeBuilder(ET.TreeBuilder):
        def comment(self, data):
            res = matchCountRE.search(data)
            if res:
                # record the count of classes that must match
                self.start(ET.Comment, {})
                self.data(res.group(1))
                self.end(ET.Comment)

    doc = ET.parse(args.classes, parser=ET.XMLParser(target=MyTreeBuilder())).getroot()

    # process results looking for both class elements and specially formatted comments
    matchCount = 0
    refClassList = None
    refClassName = None

    for child in doc:
        if isinstance(child.tag, types.FunctionType):
            # Special type used for comments
            if matchCount > 0:
                logger.log("Unexpected match request '{}': matching {} is not yet complete".format(child.text, refClassName), "E")
                ref = None
            matchCount = int(child.text)
            #print("Match count = {}".format(matchCount))

        elif child.tag == 'class':
            l = orderClass(child, logger)  # Do this so we record classes whether we match them or not.
            if matchCount > 0:
                matchCount -= 1
                className = child.attrib['name']
                if refClassName is None:
                    refClassList = l
                    refLen = len(refClassList)
                    refClassName = className
                else:
                    # compare ref list and l
                    if len(l) != refLen:
                        logger.log("Class {} (length {}) and {} (length {}) have unequal length".format(refClassName, refLen, className, len(l)), "E")
                    else:
                        errCount = 0
                        for i in range(refLen):
                            if l[i][0] != refClassList[i][0]:
                                logger.log ("Class {} and {} inconsistent order glyphs {} and {}".format(refClassName, className, refClassList[i][2], l[i][2]), "E")
                                errCount += 1
                                if errCount > 5:
                                    logger.log ("Abandoning compare between Classes {} and {}".format(refClassName, className), "E")
                                    break
                if matchCount == 0:
                    refClassName = None

    # List glyphs mentioned in classes.xml but not present in glyph_data:
    if len(missingGlyphs):
        logger.log('Glyphs mentioned in classes.xml but not present in glyph_data: ' + ', '.join(sorted(missingGlyphs)), 'W')


classes = {}  # Keep record of all classes we've seen so we can flatten references

def orderClass(classElement, logger):
    # returns a list of tuples, each containing (indexWithinClass, sortOrder, glyphName)
    # list is sorted by sortOrder
    glyphList = classElement.text.split()
    res = []
    for i in range(len(glyphList)):
        token = glyphList[i]
        if token.startswith('@'):
            # Nested class
            cname = token[1:]
            if cname in classes:
                res.extend(classes[cname])
            else:
                logger.log("Invalid fea: class {} referenced before being defined".format(cname),"S")
        else:
            # simple glyph name -- make sure it is in glyph_data:
            if token in sorts:
                res.append((i, sorts[token], token))
            else:
                missingGlyphs.add(token)

    classes[classElement.attrib['name']] = res
    return sorted(res, key=lambda x: x[1])



def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
