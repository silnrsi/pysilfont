#!/usr/bin/env python
"""classes and functions for building ftml tests from glyph_data.csv and UFO"""
__url__ = 'https://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2018 SIL International  (https://www.sil.org)'
__license__ = 'Released under the MIT License (https://opensource.org/licenses/MIT)'
__author__ = 'Bob Hallissy'

from silfont.ftml import Fxml, Ftestgroup, Ftest, Ffontsrc
from palaso.unicode.ucd import get_ucd
from itertools import product
import re
import collections.abc

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

    def __init__(self, title, logger, comment = None, fontsrc = None, fontlabel = None, fontscale = None,
                 widths = None, rendercheck = True, xslfn = None, defaultrtl = False):
        self.logger = logger
        # Initialize an Fxml object
        fxml = Fxml(testgrouplabel = "dummy")
        fxml.stylesheet = {'type': 'text/xsl', 'href': xslfn if xslfn is not None else 'ftml.xsl'}
        fxml.head.title = title
        fxml.head.comment = comment
        if isinstance(fontsrc, (tuple, list)):
            # Allow multiple fontsrc
            fxml.head.fontsrc = [Ffontsrc(fxml.head, text=fontsrc,
                                          label=fontlabel[i] if fontlabel is not None and i < len(fontlabel) else None)
                                 for i, fontsrc in enumerate(fontsrc)]
        elif fontsrc:
            fxml.head.fontsrc = Ffontsrc(fxml.head, text=fontsrc, label=fontlabel)

        if fontscale: fxml.head.fontscale = int(fontscale)
        if widths: fxml.head.widths = widths
        fxml.testgroups.pop() # Remove dummy test group
        # Save object
        self._fxml = fxml
        # Initialize state
        self._curTest = None
        self.closeTestGroup()
        self.defaultRTL = defaultrtl
        # Add first testgroup if requested
        if rendercheck:
            self.startTestGroup("Rendering Check", background="#F0F0F0")
            self.addToTest(None, "RenderingUnknown", "check", rtl = False)
            self.closeTest()
            self.closeTestGroup()

    _colorMap = {
        'aqua':    '#00ffff',
        'black':   '#000000',
        'blue':    '#0000ff',
        'fuchsia': '#ff00ff',
        'green':   '#008000',
        'grey':    '#808080',
        'lime':    '#00ff00',
        'maroon':  '#800000',
        'navy':    '#000080',
        'olive':   '#808000',
        'purple':  '#800080',
        'red':     '#ff0000',
        'silver':  '#c0c0c0',
        'teal':    '#008080',
        'white':   '#ffffff',
        'yellow':  '#ffff00',
        'orange':  '#ffa500'
    }

    @staticmethod
    def _getColor(color):
        if color is None or len(color) == 0:
            return None
        color = color.lower()
        if color in FTML._colorMap:
            return FTML._colorMap[color]
        if re.match(r'#[0-9a-f]{6}$', color):
            return color
        self.logger.log(f'Color "{color}" not understood; ignored', 'W')
        return None

    def closeTest(self, comment = None):
        if self._curTest:
            if comment is not None:
                self._curTest.comment = comment
            if self._curColor:
                self._curTest.background = self._curColor
        self._curTest = None
        self._lastUID = None
        self._lastRTL = None

    def addToTest(self, uid, s = "", label = None, comment = None, rtl = None):
        if rtl is None: rtl = self.defaultRTL
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
        features = [x for x in features if x]
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

    def setBackground(self, color):
        color = self._getColor(color)
        if color != self._curColor:
            self.closeTest()
        self._curColor = color

    def clearBackground(self):
        if self._curColor is not None:
            self.closeTest()
        self._curColor = None

    def closeTestGroup(self):
        self.closeTest()
        self._curTestGroup = None
        self._curFeatures = None
        self._curLang = None
        self._curColor = None

    def startTestGroup(self, label, background = None):
        if self._curTestGroup is not None:
            if label == self._curTestGroup.label:
                return
            self.closeTestGroup()
        # Add new test group
        self._curTestGroup = Ftestgroup(self._fxml, label = label)
        background = self._getColor(background)
        if background is not None:
            self._curTestGroup.background = background

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
        self._tvlist = None

    def __getattr__(self,name):
        if name == "tvlist":
            # tvlist is a list of all possible tag,value pairs (except the default but including None) for this feature
            # This attribute shouldn't be needed until all the possible feature value are known,
            # therefore we'll generate this the first time we need it and save it
            if self._tvlist is None:
                self._tvlist = [ None ]
                for v in range (0, self.maxval+1):
                    if v != self.default:
                        self._tvlist.append( [self.tag, str(v)])
            return self._tvlist


class FChar(object):
    """abstraction of an encoded glyph in the font"""

    def __init__(self, uids, basename, logger):
        self.logger = logger
        # uids can be a singleton integer or, for multiple-encoded glyphs, some kind of sequence of integers
        if isinstance(uids,collections.abc.Sequence):
            uids1 = uids
        else:
            uids1 = (uids,)
        # test each uid to make sure valid; remove if not.
        uids2=[]
        self.general = "unknown"
        for uid in uids1:
            try:
                gc = get_ucd(uid,'gc')
                if self.general == "unknown":
                    self.general = gc
                uids2.append(uid)
            except (TypeError, IndexError):
                self.logger.log(f'Invalid USV "{uid}" -- ignored.', 'E')
                continue
            except KeyError:
                self.logger.log('USV %04X not defined; no properties known' % uid, 'W')
        # make sure there's at least one left
        assert len(uids2) > 0, f'No valid USVs found in {repr(uids)}'
        self._uids = tuple(uids2)
        self.basename = basename
        self.feats = set()  # feat tags that affect this char
        self.langs = set()  # lang tags that affect this char
        self.aps = set()
        self.altnames = {}  # alternate glyph names.
            # the above is a dict keyed by either:
            #   lang tag e.g., 'ur', or
            #   feat tag and value, e.g., 'cv24=3'
            # and returns a the glyphname for that alternate.
        # Additional info from UFO:
        self.takesMarks = self.isMark = self.isBase = self.notInUFO = False

    # Most callers don't need to support or or care about multiple-encoded glyphs, so we
    # support the old .uid attribute by returning the first (I guess we consider it primary) uid.
    def __getattr__(self,name):
        if name == 'uids':
            return self._uids
        elif name == 'uid':
            return self._uids[0]
        else:
            raise AttributeError

    # the static method FTMLBuilder.checkGlyph is likely preferred
    #   but leave this instance method for backwards compatibility
    def checkGlyph(self, gname, font, apRE):
        # glean info from UFO if glyph is present
        if gname in font.deflayer:
            self.notInUFO = False
            for a in font.deflayer[gname]['anchor'] :
                name = a.element.get('name')
                if apRE.match(name) is None:
                    continue
                self.aps.add(name)
                if name.startswith("_") :
                    self.isMark = True
                else:
                    self.takesMarks = True
            self.isBase = self.takesMarks and not self.isMark
        else:
            self.notInUFO = True


class FSpecial(object):
    """abstraction of a ligature or other interesting sequence"""

    # Similar to FChar but takes a uid list rather than a single uid
    def __init__(self, uids, basename, logger):
        self.logger = logger
        self.uids = uids
        self.basename = basename
        # a couple of properties based on the first uid:
        try:
            self.general = get_ucd(uids[0],'gc')
        except KeyError:
            self.logger.log('USV %04X not defined; no properties known' % uids[0], 'W')
        self.feats = set()  # feat tags that affect this char
        self.aps = set()
        self.langs = set()  # lang tags that affect this char
        self.altnames = {}  # alternate glyph names.
        self.takesMarks = self.isMark = self.isBase = self.notInUFO = False

class FTMLBuilder(object):
    """glyph_data and UFO processing for building FTML"""

    def __init__(self, logger, incsv = None, fontcode = None, font = None, langs = None, rtlenable = False, ap = None ):
        self.logger = logger
        self.rtlEnable = rtlenable

        # Default diacritic base:
        self.diacBase = 0x25CC

        # Default joinBefore and joinAfter sequence
        self.joinBefore = '\u200D'  # put before a sequence to force joining shape; def = zwj
        self.joinAfter = '\u200D'   # put after a sequence to force joining shape; def = zwj

        # Dict mapping tag to Feature
        self.features = {}

        # Set of all languages seen
        if langs is not None:
            # Use a list so we keep the order (assuming caller wouldn't give us dups
            self.allLangs = list(re.split(r'\s*[\s,]\s*', langs)) # Allow comma- or space-separated tags
            self._langsComplete = True  # We have all the lang tags desired
        else:
            # use a set because the langtags are going to dribble in and be repeated.
            self.allLangs = set()
            self._langsComplete = False # Add lang_tags from glyph_data

        # Be able to find chars and specials:
        self._charFromUID = {}
        self._charFromBasename = {}
        self._specialFromUIDs = {}
        self._specialFromBasename = {}

        # list of USVs that are in the CSV but whose glyphs are not in the UFO
        self.uidsMissingFromUFO = set()

        # DummyUSV  (see charAuto())
        self.curDummyUSV = 0x100000 # Supplemental Private Use Area B

        # Compile --ap parameter
        if ap is None:
            ap = "."
        try:
            self.apRE = re.compile(ap)
        except re.error as e:
            logger.log("--ap parameter '{}' doesn't compile as regular expression: {}".format(ap, e), "S")

        if incsv is not None:
            self.readGlyphData(incsv, fontcode, font)

    def addChar(self, uids, basename):
        # Add an FChar
        # assume parameters are OK:
        c = FChar(uids, basename, self.logger)
        # fatal error if the basename or any of uids have already been seen
        fatal = False
        for uid in c.uids:
            if uid in self._charFromUID:
                self.logger.log('Attempt to add duplicate USV %04X' % uid, 'E')
                fatal = True
            self._charFromUID[uid] = c
        if basename in self._charFromBasename:
            self.logger.log('Attempt to add duplicate basename %s' % basename, 'E')
            fatal = True
        self._charFromBasename[basename] = c
        if fatal:
            self.logger.log('Cannot continue due to previous errors', 'S')
        return c

    def uids(self):
        """ returns list of uids in glyph_data """
        return self._charFromUID.keys()

    def char(self, x):
        """ finds an FChar based either basename or uid;
            generates KeyError if not found."""
        return self._charFromBasename[x] if isinstance(x, str) else self._charFromUID[x]

    def charAuto(self, x):
        """ Like char() but will issue a warning and add a dummy """
        try:
            return self._charFromBasename[x] if isinstance(x, str) else self._charFromUID[x]
        except KeyError:
            # Issue error message and create dummy Char object for this character
            if isinstance(x, str):
                self.logger.log(f'Glyph "{x}" isn\'t in glyph_data.csv - adding dummy', 'E')
                while self.curDummyUSV in self._charFromUID:
                    self.curDummyUSV += 1
                c = self.addChar(self.curDummyUSV, x)
            else:
                self.logger.log(f'Char U+{x:04x} isn\'t in glyph_data.csv - adding dummy', 'E')
                c = self.addChar(x, f'U+{x:04x}')
            return c

    def addSpecial(self, uids, basename):
        # Add an FSpecial:
        # fatal error if basename has already been seen:
        if basename in self._specialFromBasename:
            self.logger.log('Attempt to add duplicate basename %s' % basename, 'S')
        c = FSpecial(uids, basename, self.logger)
        # remember it:
        self._specialFromUIDs[tuple(uids)] = c
        self._specialFromBasename[basename] = c
        return c

    def specials(self):
        """returns a list of the basenames of specials"""
        return self._specialFromBasename.keys()

    def special(self, x):
        """ finds an FSpecial based either basename or uid sequence;
            generates KeyError if not found."""
        return self._specialFromBasename[x] if isinstance(x, str) else self._specialFromUIDs[tuple(x)]

    def _csvWarning(self, msg, exception = None):
        m = "glyph_data line {1}: {0}".format(msg, self.incsv.line_num)
        if exception is not None:
            m += '; ' + str(exception)
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
        if fl is None: self.logger.log("Empty input file", "S")
        # required columns:
        try:
            nameCol = fl.index('glyph_name');
            usvCol = fl.index('USV')
        except ValueError as e:
            self.logger.log('Missing csv input field: ' + str(e), 'S')
        except Exception as e:
            self.logger.log('Error reading csv input field: ' + str(e), 'S')
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

        next(incsv.reader, None)  # Skip first line with headers

        # RE that matches names of glyphs we don't care about
        namesToSkipRE = re.compile('^(?:[._].*|null|cr|nonmarkingreturn|tab|glyph_name)$',re.IGNORECASE)

        # RE that matches things like 'cv23' or 'cv23=4' or 'cv23=2,3'
        featRE = re.compile('^(\w{2,4})(?:=([\d,]+))?$')

        # RE that matches USV sequences for ligatures
        ligatureRE = re.compile('^[0-9A-Fa-f]{4,6}(?:_[0-9A-Fa-f]{4,6})+$')
        
        # RE that matches space-separated USV sequences
        USVsRE = re.compile('^[0-9A-Fa-f]{4,6}(?:\s+[0-9A-Fa-f]{4,6})*$')

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
            basename = gname.split('.',1)[0]

            # Process USV(s)
            # could be empty string, a single USV, space-separated list of USVs for multiple encoding,
            # or underscore-connected USVs indicating ligatures.

            usvs = line[usvCol].strip()
            if len(usvs) == 0:
                # Empty USV field, unencoded glyph
                usvs = ()
            elif USVsRE.match(usvs):
                # space-separated hex values:
                usvs = usvs.split()
                isLigature = False
            elif ligatureRE.match(usvs):
                # '_' separated hex values (ligatures)
                usvs = usvs.split('_')
                isLigature = True
            else:
                self._csvWarning(f"invalid USV field '{usvs}'; ignored")
                usvs = ()
            uids = [int(x, 16) for x in usvs]

            if len(uids) == 0:
                # Handle unencoded glyphs
                uids = None # Prevents using this record to set default feature values
                if basename in self._charFromBasename:
                    c = self._charFromBasename[basename]
                    # Check for additional AP info
                    c.checkGlyph(gname, font, self.apRE)
                elif basename in self._specialFromBasename:
                    c = self._specialFromBasename[basename]
                else:
                    self._csvWarning('unencoded variant %s found before encoded glyph' % gname)
                    c = None
            elif isLigature:
                # Handle ligatures
                c = self.addSpecial(uids, basename)
                uids = None  # Prevents using this record to set default feature values  (TODO: Research this)
            else:
                # Handle simple encoded glyphs (could be multiple uids!)
                # Create character object
                c = self.addChar(uids, basename)
                if font is not None:
                    # Examine APs to determine if this character takes marks:
                    c.checkGlyph(gname, font, self.apRE)
                    if c.notInUFO:
                        self.uidsMissingFromUFO.update(uids)

            if featCol is not None:
                feats = line[featCol].strip()
                if len(feats) > 0 and not(feats.startswith('#')):
                    feats = feats.split(';')
                    for feat in feats:
                        m = featRE.match(feat)
                        if m is None:
                            self._csvWarning('incorrectly formed feature specification "%s"; ignored' % feat)
                        else:
                            # find/create structure for this feature:
                            tag = m.group(1)
                            try:
                                feature = self.features[tag]
                            except KeyError:
                                feature = Feature(tag)
                                self.features[tag] = feature
                            # if values supplied, collect default and maximum values for this feature:
                            if m.group(2) is not None:
                                vals = [int(i) for i in m.group(2).split(',')]
                                if len(vals) > 0:
                                    if uids is not None:
                                        feature.default = vals[0]
                                    elif len(feats) == 1:  # TODO: This seems like wrong test.
                                        for v in vals:
                                            # remember the glyph name for this feature/value combination:
                                            feat = '{}={}'.format(tag,v)
                                            if c is not None and feat not in c.altnames:
                                                c.altnames[feat] = gname
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
                        for tag in re.split(r'\s*[\s,]\s*', bcp47): # Allow comma- or space-separated tags
                            c.langs.add(tag)        # lang-tags mentioned for this character
                            if not self._langsComplete:
                                self.allLangs.add(tag)  # keep track of all possible lang-tags
                    else:
                        self._csvWarning('untestable langs: no known USV')

        # We're finally done, but if allLangs is a set, let's order it (for lack of anything better) and make a list:
        if not self._langsComplete:
            self.allLangs = list(sorted(self.allLangs))

    def permuteFeatures(self, uids = None, feats = None):
        """ returns an iterator that provides all combinations of feature/value pairs, for a list of uids and/or a specific list of feature tags"""
        feats = set(feats) if feats is not None else set()
        if uids is not None:
            for uid in uids:
                if uid in self._charFromUID:
                    feats.update(self._charFromUID[uid].feats)
        l = [self.features[tag].tvlist for tag in sorted(feats)]
        return product(*l)

    @staticmethod
    def checkGlyph(obj, gname, font, apRE):
        # glean info from UFO if glyph is present
        if gname in font.deflayer:
            obj.notInUFO = False
            for a in font.deflayer[gname]['anchor']:
                name = a.element.get('name')
                if apRE.match(name) is None:
                    continue
                obj.aps.add(name)
                if name.startswith("_"):
                    obj.isMark = True
                else:
                    obj.takesMarks = True
            obj.isBase = obj.takesMarks and not obj.isMark
        else:
            obj.notInUFO = True

    @staticmethod
    def matchMarkBase(c_mark, c_base):
        """ test whether an _AP on c_mark matches an AP on c_base """
        for apM in c_mark.aps:
            if apM.startswith("_"):
                ap = apM[1:]
                for apB in c_base.aps:
                    if apB == ap:
                        return True
        return False

    def render(self, uids, ftml, keyUID = 0, addBreaks = True, rtl = None, dualJoinMode = 3, label = None, comment = None):
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
        if label is None:
            # Construct label from uids:
            label = '\n'.join(['U+{0:04X}'.format(u) for u in uids])
        if comment is None:
            # Construct comment from glyph names:
            comment = ' '.join([self._charFromUID[u].basename for u in uids])
        # see if uid list includes a mirrored char
        hasMirrored = bool(len([x for x in uids if get_ucd(x,'Bidi_M')]))
        # Analyze first and last joining char
        joiningChars = [x for x in uids if get_ucd(x, 'jt') != 'T']
        if len(joiningChars):
            # If first or last non-TRANSPARENT char is a joining char, then we need to emit examples with zwj
            # Assumes any non-TRANSPARENT char that is bc != L must be a rtl character of some sort
            uid = joiningChars[0]
            zwjBefore = (get_ucd(uid,'jt') == 'D'
                         or (get_ucd(uid,'bc') == 'L' and get_ucd(uid,'jt') == 'L')
                         or (get_ucd(uid,'bc') != 'L' and get_ucd(uid,'jt') == 'R'))
            uid = joiningChars[-1]
            zwjAfter = (get_ucd(uid,'jt') == 'D'
                         or (get_ucd(uid,'bc') == 'L' and get_ucd(uid,'jt') == 'R')
                         or (get_ucd(uid,'bc') != 'L' and get_ucd(uid,'jt') == 'L'))
        else:
            zwjBefore = zwjAfter = False
        if get_ucd(startUID,'gc') == 'Mn':
            # First char is a NSM... prefix a suitable base
            uids.insert(0, self.diacBase)
            zwjBefore = False   # No longer any need to put zwj before
        elif get_ucd(startUID, 'WSpace'):
            # First char is whitespace -- prefix with baseline brackets:
            uids.insert(0, 0xF130)
        lastNonMark = [x for x in uids if get_ucd(x,'gc') != 'Mn'][-1]
        if get_ucd(lastNonMark, 'WSpace'):
            # Last non-mark is whitespace -- append baseline brackets:
            uids.append(0xF131)
        s = ''.join([chr(uid) for uid in uids])
        if zwjBefore or zwjAfter:
            # Show contextual forms:
            # Start with isolate
            t = u'{0} '.format(s)
            if zwjBefore and zwjAfter:
                # For sequences that show dual-joining behavior, what we show depends on dualJoinMode:
                if dualJoinMode & 1:
                    # show initial, medial, final separated by space:
                    t += u'{0}{2} {1}{0}{2} {1}{0} '.format(s, self.joinBefore, self.joinAfter)
                if dualJoinMode & 2:
                    # show 3 joined forms in sequence:
                    t += u'{0}{0}{0} '.format(s)
            elif zwjAfter:
                t += u'{0}{1} '.format(s, self.joinAfter)
            elif zwjBefore:
                t += u'{1}{0} '.format(s, self.joinBefore)
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

