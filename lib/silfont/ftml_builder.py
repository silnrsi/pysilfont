#!/usr/bin/env python
from __future__ import unicode_literals
'classes and functions for building ftml tests from glyph_data.csv and UFO'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

try:
    str = unicode
    chr = unichr
except NameError: # Will  occur with Python 3
    pass
from silfont.ftml import Fxml, Ftestgroup, Ftest, Ffontsrc
from icu import Char, UCharCategory,  UCharDirection, UProperty
from itertools import product
import re

# The following should be exposed by PyICU, but does not seem to be implemented.
# UJoiningType
NON_JOINING = 0
JOIN_CAUSING = 1
DUAL_JOINING = 2
LEFT_JOINING = 3
RIGHT_JOINING = 4
TRANSPARENT = 5

# This module comprises two related functionalities:
#  1. The FTML object which acts as a staging object for ftml test data. The methods of this class
#     permit a gradual build-up of an ftml file, e.g.,
#
#       startTestGroup(...)
#       setFeatures(...)
#       addToTest(...)
#       addToTest(...)
#       clearFeatures(...)
#       setLang(...)
#       addToTest(...)
#       closeTestGroup(...)
#       ...
#       writeFile(...)
#
#     The module is clever enough, for example, to automatically close a test when changing features, languages or direction.
#
#  2. The FTMLBuilder object which reads and processes glyph_data.csv and provides assistance in iterating over
#     the characters, features, and languages that should be supported by the font, e.g.:
#
#       ftml.startTestGroup('Encoded characters')
#       for uid in sorted(builder.uids()):
#           if uid < 32: continue
#           c = builder.char(uid)
#           for featlist in builder.permuteFeatures(uids=[uid]):
#               ftml.setFeatures(featlist)
#               builder.render([uid], ftml)
#           ftml.clearFeatures()
#           for langID in sorted(c.langs):
#               ftml.setLang(langID)
#               builder.render([uid], ftml)
#           ftml.clearLang()
#
# See examples/psfgenftml.py for ideas

class FTML(object):
    """a staging class for collecting ftml content and finally writing the xml"""

    # Assumes no nesting of test groups

    def __init__(self, title, logger, comment = None, fontsrc = None, fontscale = None, widths = None, rendercheck = True, xslfn = None, defaultrtl = False):
        self.logger = logger
        # Initialize an Fxml object
        fxml = Fxml(testgrouplabel = "dummy")
        fxml.stylesheet = {'type': 'text/xsl', 'href': xslfn if xslfn is not None else 'ftml.xsl'}
        fxml.head.title = title
        fxml.head.comment = comment
        if isinstance(fontsrc, (tuple, list)):
            # Not officially part of spec to allow multiple fontsrc
            fxml.head.fontsrc = [Ffontsrc(fxml.head, text=fontsrc) for fontsrc in fontsrc]
        elif fontsrc:
            fxml.head.fontsrc = Ffontsrc(fxml.head, text = fontsrc)

        if fontscale: fxml.head.fontscale = int(fontscale)
        if widths: fxml.head.widths = widths
        fxml.testgroups.pop() # Remove dummy test group
        # Save object
        self._fxml = fxml
        # Initialize state
        self._curTest = None
        self.closeTestGroup()
        self._defaultRTL = defaultrtl
        # Add first testgroup if requested
        if rendercheck:
            self.startTestGroup("Rendering Check")
            self.addToTest(None, "RenderingUnknown", "check", rtl = False)
            self.closeTest()
            self.closeTestGroup()

    def closeTest(self, comment = None ):
        if self._curTest and comment is not None:
            self._curTest.comment = comment
        self._curTest = None
        self._lastUID = None
        self._lastRTL = None

    def addToTest(self, uid, s = "", label = None, comment = None, rtl = None):
        if rtl is None: rtl = self._defaultRTL
        if (self._lastUID and uid and uid not in range(self._lastUID, self._lastUID + 2))\
                or (self._lastRTL is not None and rtl != self._lastRTL):
            self.closeTest()
        self._lastUID = uid
        self._lastRTL = rtl
        if self._curTestGroup is None:
            # Create a new Ftestgroup
            self.startTestGroup("Group")
        if self._curTest is None:
            # Create a new Ftest
            if label is None:
                label = "U+{0:04X}".format(uid) if uid is not None else "test"
            test = Ftest(self._curTestGroup, label = label, string = '')
            if comment:
                test.comment = comment
            if rtl: test.rtl = "True"
            # Construct stylename and add style if needed:
            x = ['{}_{}'.format(t,v) for t,v in self._curFeatures.items()] if self._curFeatures else []
            if self._curLang:
                x.insert(0,self._curLang)
            if len(x):
                test.stylename = '_'.join(x)
                self._fxml.head.addstyle(test.stylename, feats = self._curFeatures, lang = self._curLang)
            # Append to current test group
            self._curTestGroup.tests.append(test)
            self._curTest = test
        if len(self._curTest.string): self._curTest.string += ' '
        # Special hack until we get to python3 with full unicode support
        self._curTest.string += ''.join([ c if ord(c) < 128 else '\\u{0:06X}'.format(ord(c)) for c in s ])
        # self._curTest.string += s

    def setFeatures(self, features):
        # features can be None or a list; list elements can be:
        #   None
        #   a feature setting in the form [tag,value]
        if features is None:
            return self.clearFeatures()
        features = [x for x in features if x is not None]
        if len(features) == 0:
            return self.clearFeatures()
        features = dict(features)   # Convert to a dictionary -- this is what we'll keep.
        if features != self._curFeatures:
            self.closeTest()
        self._curFeatures = features

    def clearFeatures(self):
        if self._curFeatures is not None:
            self.closeTest()
        self._curFeatures = None

    def setLang(self, langID):
        if langID != self._curLang:
            self.closeTest();
        self._curLang = langID

    def clearLang(self):
        if self._curLang:
            self.closeTest()
        self._curLang = None

    def closeTestGroup(self):
        self.closeTest()
        self._curTestGroup = None
        self._curFeatures = None
        self._curLang = None

    def startTestGroup(self, label):
        if self._curTestGroup is not None:
            if label == self._curTestGroup.label:
                return
            self.closeTestGroup()
        # Add new test group
        self._curTestGroup = Ftestgroup(self._fxml, label = label)
        # append to root test groups
        self._fxml.testgroups.append(self._curTestGroup)

    def writeFile(self, output):
        self.closeTestGroup()
        self._fxml.save(output)


class Feature(object):
    """abstraction of a feature"""

    def __init__(self, tag):
        self.tag = tag
        self.default = 0
        self.maxval = 1

    def __getattr__(self,name):
        if name == "tvlist":
            # tvlist is a list of all possible tag,value pairs (except the default but including None) for this feature
            # We'll generate this the first time we need it and save it
            self.tvlist = [ None ]
            for v in range (0, self.maxval+1):
                if v != self.default:
                    self.tvlist.append( [self.tag, str(v)])
            return self.tvlist


class FChar(object):
    """abstraction of a character in the font"""

    def __init__(self, uid, basename, logger):
        self.logger = logger
        self.uid = uid
        self.basename = basename
        if Char.isdefined(uid):
            self.general = Char.charType(uid)
            self.cc = Char.getCombiningClass(uid)
            self.icuGC = Char.charType(uid)
            self.icuJT = Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE)
        else:
            self.logger.log('USV %04X not in ICU; no properties known' % uid, 'W')
        self.feats = set()  # feat tags that affect this char
        self.langs = set()  # lang tags that affect this char
        # Additional info from UFO:
        self.takesMarks = self.isMark = self.isBase = False

    def checkAPs(self, gname, font, apRE):
        # glean info from UFO
        if gname in font.deflayer:
            for a in font.deflayer[gname]['anchor'] :
                name = a.element.get('name')
                if apRE.match(name) is None:
                    continue
                if name.startswith("_") :
                    self.isMark = True
                else:
                    self.takesMarks = True
            self.isBase = self.takesMarks and not self.isMark


class FSpecial(object):
    """abstraction of a ligature or other interesting sequence"""

    # Similar to FChar but takes a uid list rather than a single uid
    def __init__(self, uids, basename, logger):
        self.logger = logger
        self.uids = uids
        self.basename = basename
        if Char.isdefined(uids[0]):
            self.general = Char.charType(uids[0])
            self.cc = Char.getCombiningClass(uids[0])
        else:
            self.logger.log('USV %04X not in ICU; no properties known' % uids[0], 'W')
        self.feats = set()  # feat tags that affect this char
        self.langs = set()  # lang tags that affect this char


class FTMLBuilder(object):
    """glyph_data and UFO processing for building FTML"""

    def __init__(self, logger, incsv = None, fontcode = None, font = None, rtlenable = False, ap = None ):
        self.logger = logger
        self.rtlEnable = rtlenable

        # Default diacritic base:
        self.diacBase = 0x25CC

        # Dict mapping tag to Feature
        self.features = {}
        # Be able to find chars and specials:
        self._charFromUID = {}
        self._charFromBasename = {}
        self._specialFromBasename = {}

        # Compile --ap parameter
        if ap is None:
            ap = "."
        try:
            self.apRE = re.compile(ap)
        except re.error as e:
            logger.log("--ap parameter '{}' doesn't compile as regular expression: {}".format(ap, e), "S")

        if incsv is not None:
            self.readGlyphData(incsv, fontcode, font)

    def addChar(self, uid, basename):
        # add an FChar:
        # fatal error if uid or basename has already been seen:
        if uid in self._charFromUID:
            self.logger.log('Attempt to add duplicate USV %04X' % uid, 'S')
        if basename in self._charFromBasename:
            self.logger.log('Attempt to add duplicate basename %s' % basename, 'S')

        c = FChar(uid, basename, self.logger)
        # remember it:
        self._charFromUID[uid] = c
        self._charFromBasename[basename] = c
        return c

    def uids(self):
        return self._charFromUID.keys()

    def char(self, uid):
        return self._charFromUID[uid]

    def addSpecial(self, uids, basename):
        # Add an FSpecial:
        # fatal error if basename has already been seen:
        if basename in self._specialFromBasename:
            self.logger.log('Attempt to add duplicate basename %s' % basename, 'S')
        c = FSpecial(uids, basename, self.logger)
        # remember it:
        self._specialFromBasename[basename] = c
        return c

    def specials(self):
        return self._specialFromBasename.keys()

    def special(self, basename):
        return self._specialFromBasename[basename]


    def _csvWarning(self, msg, exception = None):
        m = "glyph_data line {1}: {0}".format(msg, self.incsv.line_num)
        if exception is not None:
            m += '; ' + exception.message
        self.logger.log(m, 'W')

    def readGlyphData(self, incsv, fontcode = None, font = None):
        # Remember csv file for other methods:
        self.incsv = incsv

        # Validate fontcode, if provided
        if fontcode is not None:
            whichfont = fontcode.strip().lower()
            if len(whichfont) != 1:
                self.logger.log('fontcode must be a single letter', 'S')
        else:
            whichfont = None

        # Get headings from csvfile:
        fl = incsv.firstline
        if fl is None: self.logger.log("Empty imput file", "S")
        # required columns:
        try:
            nameCol = fl.index('glyph_name');
            usvCol = fl.index('USV')
        except ValueError as e:
            self.logger.log('Missing csv input field: ' + e.message, 'S')
        except Exception as e:
            self.logger.log('Error reading csv input field: ' + e.message, 'S')
        # optional columns:
        # If -f specified, make sure we have the fonts column
        if whichfont is not None:
            if 'Fonts' not in fl: self.logger.log('-f requires "Fonts" column in glyph_data', 'S')
            fontsCol = fl.index('Fonts')
        # Allow for projects that use only production glyph names (ps_name same as glyph_name)
        psCol = fl.index('ps_name') if 'ps_name' in fl else nameCol
        # Allow for projects that have no feature and/or lang-specific behaviors
        featCol = fl.index('Feat') if 'Feat' in fl else None
        bcp47Col = fl.index('bcp47tags') if 'bcp47tags' in fl else None

        next(incsv.reader, None)  # Skip first line with headers in

        # RE that matches names of glyphs we don't care about
        namesToSkipRE = re.compile('^(?:[._].*|null|cr|nonmarkingreturn|tab|glyph_name)$',re.IGNORECASE)

        # RE that matches things like 'cv23' or 'cv23=4' or 'cv23=2,3'
        featRE = re.compile('^(\w{2,4})(?:=([\d,]+))?$')

        # keep track of glyph names we've seen to detect duplicates
        namesSeen = set()
        psnamesSeen = set()

        # OK, process all records in glyph_data
        for line in incsv:
            gname = line[nameCol].strip()

            # things to ignore:
            if namesToSkipRE.match(gname):
                continue
            if whichfont is not None and line[fontsCol] != '*' and line[fontsCol].lower().find(whichfont) < 0:
                continue
            if len(gname) == 0:
                self._csvWarning('empty glyph name in glyph_data; ignored')
                continue
            if gname.startswith('#'):
                continue
            if gname in namesSeen:
                self._csvWarning('glyph name %s previously seen in glyph_data; ignored' % gname)
                continue

            psname = line[psCol].strip() or gname   # If psname absent, working name will be production name
            if psname in psnamesSeen:
                self._csvWarning('psname %s previously seen; ignored' % psname)
                continue
            namesSeen.add(gname)
            psnamesSeen.add(psname)

            # compute basename-- the glyph name without extensions:
            i = gname.find('.',1)
            basename = gname if i <= 0 else gname[:i]

            # Process USV
            # could be empty string, a single USV or space-separated list of USVs
            try:
                uidList = [int(x, 16) for x in line[usvCol].split()]
            except Exception as e:
                self._csvWarning("invalid USV '%s' (%s); ignored: " % (line[usvCol], e.message))
                uidList = []

            if len(uidList) == 1:
                # Handle simple encoded glyphs
                uid = uidList[0]
                if uid in self._charFromUID:
                    self._csvWarning('USV %04X previously seen; ignored' % uid)
                    uidList = []
                else:
                    # Create character object for this USV
                    c = self.addChar(uid, basename)
                if font is not None:
                    # Examine APs to determine if this character takes marks:
                    c.checkAPs(gname, font, self.apRE)
            elif len(uidList) > 1:
                # Handle ligatures
                c = self.addSpecial(uidList, basename)
                uid = None

            if len(uidList) == 0:
                # Handle unencoded glyphs
                uid = None
                if basename in self._charFromBasename:
                    c = self._charFromBasename[basename]
                    # Check for additional AP info
                    c.checkAPs(gname, font, self.apRE)
                elif basename in self._specialFromBasename:
                    c = self._specialFromBasename[basename]
                else:
                    self._csvWarning('unencoded variant %s found before encoded glyph' % gname)
                    c = None

            if featCol is not None:
                feats = line[featCol].strip()
                if len(feats) > 0 and not(feats.startswith('#')):
                    for feat in feats.split(';'):
                        m = featRE.match(feat)
                        if m is None:
                            self._csvWarning('incorrectly formed feature specification "%s"; ignored' % feat)
                        else:
                            # create/find structure for this feature:
                            tag = m.group(1)
                            feature = self.features.setdefault(tag,Feature(tag))
                            # if values supplied, collect default and maximum values for this feature:
                            if m.group(2) is not None:
                                vals = [int(i) for i in m.group(2).split(',')]
                                if len(vals) > 0:
                                    if uid is not None: feature.default = vals[0]
                                    vals.append(feature.maxval)
                                    feature.maxval = max(vals)
                            if c is not None:
                                # Record that this feature affects this character:
                                c.feats.add(tag)
                            else:
                                self._csvWarning('untestable feature "%s" : no known USV' % tag)

            if bcp47Col is not None:
                bcp47 = line[bcp47Col].strip()
                if len(bcp47) > 0 and not(bcp47.startswith('#')):
                    if c is not None:
                        for tag in bcp47.split(','):
                            c.langs.add(tag.strip())
                    else:
                        self._csvWarning('untestable langs: no known USV')

    def permuteFeatures(self, uids = None, feats = None):
        """ returns an iterator that provides all combinations of feature/value pairs, either for a list of uids or a specific list of featIDs"""
        feats = set(feats) if feats is not None else set()
        if uids is not None:
            for uid in uids:
                if uid in self._charFromUID:
                    feats.update(self._charFromUID[uid].feats)
        l = [self.features[tag].tvlist for tag in sorted(feats)]
        return product(*l)

    def render(self, uids, ftml, keyUID = 0, addBreaks = True, rtl = None):
        """ general purpose (but not required) function to generate ftml for a character sequence """
        if len(uids) == 0:
            return
        # Make a copy so we don't affect caller
        uids = list(uids)
        # Remember first uid and original length for later
        startUID = uids[0]
        uidLen = len(uids)
        # if keyUID wasn't supplied, use startUID
        if keyUID == 0: keyUID = startUID
        # Construct label from uids:
        label = '\n'.join(['U+{0:04X}'.format(u) for u in uids])
        # Construct comment from glyph names:
        comment = ' '.join([self._charFromUID[u].basename for u in uids])
        # see if uid list includes a mirrored char
        hasMirrored = bool(len([x for x in uids if Char.isMirrored(x)]))
        # Analyze first and last joining char
        joiningChars = [x for x in uids if Char.getIntPropertyValue(x, UProperty.JOINING_TYPE) != TRANSPARENT]
        if len(joiningChars):
            # If first or last non-TRANSPARENT char is a joining char, then we need to emit examples with zwj
            uid = joiningChars[0]
            zwjBefore = Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE) == DUAL_JOINING or (
                            Char.charDirection(uid) == UCharDirection.LEFT_TO_RIGHT and
                            Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE) == LEFT_JOINING) or (
                            Char.charDirection(uid) != UCharDirection.LEFT_TO_RIGHT and
                            Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE) == RIGHT_JOINING)
            uid = joiningChars[-1]
            zwjAfter = Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE) == DUAL_JOINING or (
                            Char.charDirection(uid) == UCharDirection.LEFT_TO_RIGHT and
                            Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE) == RIGHT_JOINING) or (
                            Char.charDirection(uid) != UCharDirection.LEFT_TO_RIGHT and
                            Char.getIntPropertyValue(uid, UProperty.JOINING_TYPE) == LEFT_JOINING)
        else:
            zwjBefore = zwjAfter = False
        if Char.charType(startUID) == UCharCategory.NON_SPACING_MARK:
            # First char is a NSM... prefix a suitable base
            uids.insert(0, self.diacBase)
            zwjBefore = False   # No longer any need to put zwj before
        elif Char.isUWhiteSpace(startUID):
            # First char is whitespace -- prefix with baseline brackets:
            uids.insert(0, 0xF130)
        lastNonMark = [x for x in uids if Char.charType(x) != UCharCategory.NON_SPACING_MARK][-1]
        if Char.isUWhiteSpace(lastNonMark):
            # Last non-mark is whitespace -- append baseline brackets:
            uids.append(0xF131)
        s = ''.join([chr(uid) for uid in uids])
        if zwjBefore or zwjAfter:
            # Show contextual forms:
            t = u'{0} '.format(s)
            if zwjAfter:
                t += u'{0}\u200D '.format(s)
                if zwjBefore:
                    t += u'\u200D{0}\u200D '.format(s)
            if zwjBefore:
                t += u'\u200D{0} '.format(s)
            if zwjBefore and zwjAfter:
                t += u'{0}{0}{0}'.format(s)
            if addBreaks: ftml.closeTest()
            ftml.addToTest(keyUID, t, label = label, comment = comment, rtl = rtl)
            if addBreaks: ftml.closeTest()
        elif hasMirrored and self.rtlEnable:
            # Contains mirrored and rtl enabled:
            if addBreaks: ftml.closeTest()
            ftml.addToTest(keyUID, u'{0} LTR: \u202A{0}\u202C RTL: \u202B{0}\u202C'.format(s), label = label, comment = comment, rtl = rtl)
            if addBreaks: ftml.closeTest()
        # elif is LRE, RLE, PDF
        # elif is LRI, RLI, FSI, PDI
        elif uidLen > 1:
            ftml.addToTest(keyUID, s , label = label, comment = comment, rtl = rtl)
        else:
            ftml.addToTest(keyUID, s , comment = comment, rtl = rtl)

