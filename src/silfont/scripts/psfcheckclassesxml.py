#!/usr/bin/env python3
'''integrety checking for classes defined in xml

Identify potential typos in an XML class definition file by comparing glyphnames with font and glyph_data.
Verify specially-identified classes defined in xml have correct length and, if desired, correct ordering.
'''
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2019-2026, SIL Global (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

import re
import types
from xml.etree import ElementTree as ET
from silfont.core import execute
import glob
import os.path
import re
from fontParts.world import OpenFont
from fontTools import ttLib

argspec = [
    ('classes', {'help': 'Class definition in XML format', 'nargs': '?', 'default': 'classes.xml'}, {'type': 'filename'}),
    ('glyphdata', {'help': 'Glyph info csv file', 'nargs': '?', 'default': 'glyph_data.csv'}, {'type': 'incsv'}),
    ('-f', '--font', {'help': 'TTF or UFO input font for improved checking', 'default': None}, {}),
    ('--gname',  {'help': 'Column header for glyph working name', 'default': 'glyph_name'}, {}),
    ('--psname', {'help': 'Column header for ps_name', 'default': 'ps_name'}, {}),
    ('--sort',   {'help': 'Column header(s) for sort order'}, {}),
    ('--filter', {'help': "Include only interesting names (identified by optional regex) for some reporting purposes",'nargs': '?', 'const': r'^[^_]'}, {}),
    ('-g', '--graphite', {'help': 'Include graphite class order testing', 'action': 'store_true'},{}),
]

# Dictionary of {glyphName : sortValue, ...} built from glyph_data.csv or a TTF (if supplied)
sortvalue = dict()

# Keep track of glyphs mentioned in classes but not in glyph_data.csv or not in the input font
missingCSVGlyphs = set()    # Glyphs mentioned in a class but not in glyph_data.csv
missingFontGlyphs = set()   # Glyphs mentioned in a class but not in the font

missingCSVSort = set()      # Glyphs that have missing or invalid sort orders in glyph_data.csv
missingUsedSort = set()     # Glyphs with missing or invalid sort orders actually used in matching classes

fontGnames = set()          # Glyph names extracted from the font
csvGnames = set()           # Glyph names extracted from glyph_data.csv
classesGnames = set()       # Glyph names extracted from classes.xml

def doit(args):
    logger = args.logger

    # The following globals are sometimes replaced entirely, and because they are
    # referenced in orderClass() we need to indicate they are global.
    global fontGnames, csvGnames, sortvalue

    # Parse args.filter if provided
    if args.filter:
        try:
            filter = re.compile(args.filter)
        except Exception as E:
            logger.log(f"Invalid regex given for --filter: '{args.filter}': {E}", "S")
    else:
        # If not provided, use a regex that selects all glyphs.
        filter = re.compile(r'.')


    # calculate path to classes file to use in case we aren't in `source/` folder
    try:
        classesDirname = os.path.dirname(args.classes)
    except Exception as E:
        logger.log(f"Invalid classes filename: '{args.classes}': {E}", "S")

    def trytoopenfont(pattern):
        # Given a pathname pattern (glob) that ends with either `.ttf` or `.ufo`,
        # try to open that path as a font.
        # Returns tuple type ('ttf' or 'ufo'), font object, font filename
        # or, if there is an error: (None, error message, None)
        try:
            fontfilename = glob.glob(pattern)[0]
            # Figure out whether we have a UFO or TTF to examine:
            if (re.match(r'.*\.ttf$', fontfilename, re.IGNORECASE)):
                font = ttLib.TTFont(fontfilename)
                logger.log(f"Opening TTF for input: {fontfilename}", "P")
                return 'ttf', font, fontfilename
            if (re.match(r'.*\.ufo/?$', fontfilename, re.IGNORECASE)):
                font = OpenFont(fontfilename)
                logger.log(f"Opening UFO for input: {fontfilename}", "P")
                skipExport = font.lib.get('public.skipExportGlyphs', [])
                
                return 'ufo', font, fontfilename
            return None, f"unrecognized font type; file: {fontfilename}", None
        except Exception as E:
            return None, str(E), None

    # Find a suitable font:
    #   Use args.font if provided. 
    #   Otherwise search, in order:
    #       {ClassesDirname}/../results/ 
    #       {ClassesDirname}/masters/
    #       {ClassesDirname}/
    #  for the first available "Regular" ttf or UFO.
    if args.font:
        (fontType, font, fontfilename) = trytoopenfont(args.font)
        if fontType is None:
            logger.log(f"Cannot open '{args.font}' as either UFO or TTF: {font}", "S")
    else:
        # No font argument provided... see if we can find a TTF in results/ or a UFO in source/
        for pattern in (os.path.join(classesDirname, '../results/*-Regular.ttf'), 
                        os.path.join(classesDirname, 'masters/*-Regular.ufo'),
                        os.path.join(classesDirname, '*-Regular.ufo')):
            (fontType, font, fontfilename) = trytoopenfont(pattern)
            if fontType is not None:
                break
        if fontType is None:
            logger.log(f"Cannot find default UFO or TTF font; please specify --font parameter", "S")


    # Read input csv to get glyph sort order and reverse name map
    incsv = args.glyphdata
    fl = incsv.firstline
    if fl is None: logger.log(f"Empty input csv file '{args.glyphdata}'", "S")
    numfields = len(fl)
    if numfields > 1:  # More than 1 column, so must have headers  
        # In general, don't indicate errors for missing data but just set the
        # relevant `*pos` variable to None
        try:
            glyphnpos = fl.index(args.gname)
        except ValueError:
            glyphnpos = None
        try:
            psnamepos = fl.index(args.psname)
        except ValueError:
            psnamepos = None
        
        # Determine which column defines sort order, either by what the user provided or trying known headers:
        if args.sort:
            # User provided sort column header:
            try:
                sortpos = fl.index(args.sort)
            except ValueError:
                logger.log("Column '{args.sort}' is not present in glyph_data.csv", "W")
                sortpos = None
        else:
            # Try the known sort column headers:
            sortpos = None
            for h in ('sort_final', 'DesignerOrder', 'sort_final_cdg'):
                try:
                    sortpos = fl.index(h)
                    logger.log(f"Using column '{h}' for sort order info", "I")
                    break
                except ValueError:
                    continue

        # Possible error concerns:
        if glyphnpos is None:
            # no glyph_name header
            if psnamepos is None:
                logger.log(f"Columns '{args.gname}' and '{args.psname}' cannot both omitted from glyph_data.csv", "S")
            else:
                # Just one glyph name column -- use it but don't pretend there are two name cols
                glyphnpos = psnamepos
                psnamepos = None
        if args.graphite and fontType == 'ufo' and sortpos is None:
            logger.log(f"For --graphite, glyph order info must be in glyph_data.csv if the input font is a UFO", "S")
        needNameMap = fontType == 'ttf' and glyphnpos is not None and psnamepos is not None
        if needNameMap:
            nameMap=dict()

        # process rest of multi-column CSV
        next(incsv.reader, None)  # Skip first line with containing headers
        for line in incsv:
            glyphn = line[glyphnpos]
            if len(glyphn) == 0 or glyphn.startswith('#'):
                continue	# No need to include cases where name is blank or a comment
            
            # Save glyphname
            csvGnames.add(glyphn)
            # check and save sortvalue if provided
            if sortpos is not None:
                if re.match(r'[0-9.]+', line[sortpos]):
                    # Looks like sort value -- starts with a number (at least not blank or non-numeric)
                    sortvalue[glyphn] = float(line[sortpos])
                else:
                    # invalid or missing sort value
                    # Only a problem if glyph used is in matching classes and we're checking for graphite fonts
                    sortvalue[glyphn] = -1
                    missingCSVSort.add(glyphn)
            # construct nameMape if needed
            if needNameMap:
                # Be able to find working glyph name from the production one in the TTF:
                nameMap[line[psnamepos]] = glyphn
    
    elif numfields == 1:   # Simple text file.  Create sortvalue in same format as for csv files
        # first create a list (in file order) of glyph names that are not null or a comment
        csvGnames = [x[0] for x in incsv if len(x[0]) > 0 and not x[0].startswith('#')]
        # Create a dictionary from which to lookup a numeric sort order
        sortvalue = dict(zip(csvGnames, range(len(csvGnames))))
        # Convert glyphlist to set
        csvGnames = set(csvGnames)
        needNameMap = False

    else:
        logger.log("Invalid csv file", "S")
    
    # Get set of glyphs in the font
    #    For TTFs, use nameMap to get friendly glyphname; create a sortvalue dictionary from actual glyph order.
    if fontType == 'ttf':
        fontGnames = font.getGlyphOrder()    
        if needNameMap:
            # where possible, map TTF glyph names ("production" or PS Names) back through glyph_data to get working names.
            fontGnames = [nameMap.get(x, x) for x in fontGnames]
        # Overwrite sortvalue dictionary with one based on actual font order
        sortvalue = dict(zip(fontGnames, range(len(fontGnames))))
        fontGnames = set(fontGnames)
    else:
        fontGnames = set(font.defaultLayer.keys()) - set(font.lib.get('public.skipExportGlyphs', []))
    # Done with font
    font.close()

    # Finally, we're ready to process all the classes in the input xml file:

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

    try:
        logger.log(f"Opening class definition file: {args.classes}", 'P')
        doc = ET.parse(args.classes, parser=ET.XMLParser(target=MyTreeBuilder())).getroot()
    except Exception as inst:
        logger.log(f"Error parsing classes file '{args.classes}': {inst}", "S")

    # process the results, looking for class elements and specially formatted comments

    matchCount = 0
    refClassList = None
    refClassName = None

    for child in doc:
        if isinstance(child.tag, types.FunctionType):
            # Special type used for comments
            if matchCount > 0:
                logger.log(f"Unexpected match request '{child.text}': matching '{refClassName}' is not yet complete", "E")
                ref = None
            matchCount = int(child.text)
            #print(f"Match count = {matchCount}")

        elif child.tag == 'class':
            # Record this class (whether we match them or not) in case they are nested within another class
            l = orderClass(child, logger)  
            # Are we trying to match classes?
            if matchCount > 0:
                # Okay we're matching classes!
                matchCount -= 1
                className = child.attrib['name']
                classFixed = child.attrib.get('fixed', None)  # Retrieve `fixed` attribute if provided

                # Keep a record of glyphs used in matching classs that do not have legitimate sort values:
                missingUsedSort.update(x[2] for x in l if x[1] < 0)

                if refClassName is None:
                    # This is first class in the match sequence so it is the reference
                    refClassList = l
                    refLen = len(refClassList)
                    refClassName = className
                    refClassFixed = classFixed
                    if doGraphite := args.graphite:
                        # User has requested graphite order checking. Can we do it?
                        if refClassFixed is not None:
                            doGraphite = False  # Nope. Give warning:
                            logger.log (f"Class '{className}' includes 'fixed' attribute; graphite ordering checks will not be attempted.", "W")                    
                else:
                    # compare ref class with this one
                    if len(l) != refLen:
                        logger.log(f"Class '{refClassName}' (length {refLen}) and '{className}' (length {len(l)}) have unequal length", "E")
                    elif doGraphite:
                        if classFixed is not None:
                            logger.log (f"Class '{className}' includes 'fixed' attribute; abandoning graphite ordering checks.", "W")
                            doGraphite = False
                        else:
                            # Verify the classes line up the same way when sorted by glyphID -- needed for Graphite fonts
                            errCount = 0
                            for i in range(refLen):
                                if l[i][0] != refClassList[i][0]:
                                    logger.log (f"Class '{refClassName}' and '{className}' inconsistent order glyphs '{refClassList[i][2]}' and '{l[i][2]}'", "E")
                                    errCount += 1
                                    if errCount > 5:
                                        logger.log (f"Abandoning compare between Classes '{refClassName}' and '{className}'", "E")
                                        break
                if matchCount == 0:
                    refClassName = None

    # List glyphs mentioned in classes.xml but not present in glyph_data:
    if len(missingCSVGlyphs):
        logger.log('Glyphs mentioned in classes.xml but not present in glyph_data:' + makeLines(sorted(missingCSVGlyphs)), 'W')
    # List glyphs mentioned in classes.xml but not present in the font:
    if len(missingFontGlyphs):
        logger.log(f'Glyphs mentioned in classes.xml but not present in {fontType.upper()}:' + makeLines(sorted(missingFontGlyphs)), 'W')
    # List "interesting glyphs" that are in the font but not in glyph_data:
    interesting = [g for g in (fontGnames - csvGnames) if filter.search(g)]
    if len(interesting):
        logger.log(f'Interesting glyphs in the {fontType.upper()} but not in glyph_data:' + makeLines(sorted(interesting)), 'I')
    # List interesting glyphs that are in glyph_data but not classes (i.e. candidates for typos in classes):
    interesting = [g for g in (csvGnames - classesGnames) if filter.search(g)]
    if len(interesting):
        logger.log(f'Interesting glyphs in glyph_data but not in classes.xml:' + makeLines(sorted(interesting)), 'I')
    
    # Possible problems that relate only to Graphite                   
    if args.graphite:
        if len(missingUsedSort):
            logger.log('Glyphs used in matching classes that have no sort value:' + makeLines(sorted(missingUsedSort)), 'W')
        if len(missingCSVSort):
            logger.log('Glyphs in glyph_data that have no sort value: '+ makeLines(sorted(missingCSVSort)), 'W')
    

classes = {}  # Keep record of all classes we've seen so we can flatten references

glyphNameRE = re.compile(r'\.notdef|[a-zA-Z]|[a-zA-Z_][a-zA-Z0-9_.*+:^|~-]+')
classNameRE = re.compile(r'[a-zA-Z][a-zA-Z0-9_.-]*')

def orderClass(classElement, logger):
    # returns a list of tuples, each containing (indexWithinClass, sortOrder, glyphName)
    # list is sorted by sortOrder
    className = classElement.attrib['name']
    if className in classes:
        logger.log(f"Invalid class definition file: class '{className}' defined more than once","E")
    if not classNameRE.fullmatch(className):
        logger.log(f"Invalid class name: '{className}'","E")

    # First, build and save a list of tupples, (sortOrder, GlyphName), ordered by
    # their appearance in the classElement, flattening any referenced classes as needed.
    res = []
    # The following iteration (over tokens then exts) is modeled after what make_gdl (more precisely, Font::TTF::Scripts::AP.pl) does.
    # See https://github.com/silnrsi/font-ttf-scripts/blob/e38c356718224688893e546ecf294834b79aa68c/lib/Font/TTF/Scripts/AP.pm#L529-L585
    for token in classElement.text.split():
        if token.startswith('@'):
            # Nested class
            cname = token[1:]
            if cname in classes:
                res.extend(classes[cname])
            else:
                logger.log(f"Invalid class definition file: class '{cname}' referenced before being defined; reference ignored","E")
            continue
        # Not a class, thus should be a glyph name
        for ext in [''] + classElement.get('exts', '').split():
            g = token + ext
            if not glyphNameRE.fullmatch(g):
                logger.log(f"Invalid glyph working name: class '{className}' glyph '{g}'", 'E')
            if g in fontGnames:
                # Add this glyph to the class, but use an invalid sort if sortvalue for this glyph is unknown
                res.append((sortvalue.get(g, -1), g))
                # Remember this as a name seen in classes file
                classesGnames.add(g)
                # if not in csv, add to missing
                if g not in csvGnames:
                    missingCSVGlyphs.add(g)
            # else....
            # Glyphnames that are not in the font will be silently ignored by the toolchain,
            #    so we won't add them to the class.
            # If glyphname was constructed from a base + ext, we'll completely ignore it.
            # But in initial iteration, wheren ext=='', we mark that as a missing glyph.
            elif ext=='':
                classesGnames.add(g)
                missingFontGlyphs.add(g)
                if g not in csvGnames:
                    missingCSVGlyphs.add(g)

    #  Save the (sortOrder, GlyphName) tuple list in case this class is referenced later.
    classes[className] = res

    # Now create a list of tupples (classIndex, sortOrder, GlyphName)
    res = [(i,)+ res[i] for i in range(len(res))]
    # and sort by sortOrder
    return sorted(res, key=lambda x: x[1])

def makeLines(glist):
    """break list of glyphnames into indented lines for output"""
    lines = ""
    indent = "\n     "
    while len(glist):
        line = ""
        while len(glist) and len(line) < 80:
            gname = glist.pop(0)
            line = f'{line}{gname} '
        if len(line):
            lines = f"{lines}{indent}{line}"
            line = ""     
    return lines


def cmd() : execute(None,doit,argspec)
if __name__ == "__main__": cmd()
