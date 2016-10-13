#!/usr/bin/env python
'Classes and functions for use handling FTML objects in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from xml.etree import cElementTree as ET
import os
#import sys, os, copy, shutil, filecmp
import silfont.core
import silfont.etutil as ETU

class Fxml(ETU.ETelement) :
    def __init__(self, file = None, xmlstring = None, logger = None, params = None) :
        self.logger = logger if logger is not None else silfont.core.loggerobj()
        self.params = params if params is not None else silfont.core.parameters()
        self.parseerrors=None
        if file and xmlstring : self.logger.log("Can't specify both file and xmlstring","X")
        if not (file or xmlstring) : # Create minimal valid ftml
            xmlstring = '<ftml version="1.0"><head></head><testgroup label="main"></testgroup></ftml>'

        try :
            if file :                                   ## Need to also get the style info from the xml processing instructions
                self.element = ET.parse(file).getroot() ## Not supported by cElementTree (or elementtree)
            else :
                self.element = ET.fromstring(xmlstring)
        except Exception as e :
            self.logger.log("Error parsing FTML input: " + str(e), "S")

        super(Fxml,self).__init__(self.element)

        self.version = getattrib(self.element,"version")
        if self.version != "1.0" : self.logger.log("ftml items must have a version of 1.0", "S")

        self.process_subelements((
            ("head",      "head"      , Fhead,     True, False),
            ("testgroup", "testgroups", Ftestgroup, True, True )),
            offspec = False)

        if self.parseerrors:
            self.logger.log("Errors parsing ftml element:","E")
            for error in self.parseerrors : self.logger.log("  " + error,"E")
            self.logger.log("Invalid FTML", "S")


class Fhead(ETU.ETelement) :
    def __init__(self, element) :
        super(Fhead,self).__init__(element)
        self.process_subelements((
            ("comment",    "comment",    None,          False, False),
            ("fontscale",  "fontscale",  None,          False, False),
            ("fontsrc",    "fontsrc",    Ffontsrc,      False, False),
            ("styles",     "styles",     ETU.ETelement, False, False ),
            ("title",      "title",      None,          False, False),
            ("widths",     "widths",     _Fwidth,        False, False)),
            offspec = True)

        if self.fontscale is not None : self.fontscale = int(self.fontscale)
        if self.styles is not None :
            styles = []
            for styleelem in self.styles["style"] :
                style = Fstyle(styleelem)
                styles.append(style)
                if style.parseerrors:
                    name = "" if style.name is None else style.name
                    self.parseerrors.append("Errors parsing style element: " + name)
                    for error in style.parseerrors : self.parseerrors.append("  " + error)
            self.styles = styles
        if self.widths is not None : self.widths = self.widths.widthsdict # Convert _Fwidths object into dict


class Ffontsrc(ETU.ETelement) :
    def __init__(self, element) :
        super(Ffontsrc,self).__init__(element)
        self.text = self.element.text

class Fstyle(ETU.ETelement) :
    def __init__(self, element) :
        super(Fstyle,self).__init__(element)
        self.process_attributes((
            ("feats", "feats", False),
            ("lang",  "lang",  False),
            ("name",  "name",  True)),
            others = False)

class _Fwidth(ETU.ETelement) : # Only used temporarily whilst pasing xml
    def __init__(self, element) :
        super(_Fwidth,self).__init__(element)
        self.process_attributes((
            ("comment", "comment", False),
            ("label", "label", False),
            ("string", "string", False),
            ("stylename", "stylename", False),
            ("table",  "table",  False)),
            others = False)
        self.widthsdict = {
            "comment": self.comment,
            "label": self.label,
            "string": self.string,
            "stylename": self.stylename,
            "table": self.table}

class Ftestgroup(ETU.ETelement) :
    def __init__(self, element) :
        super(Ftestgroup,self).__init__(element)
        self.process_attributes((("label", "label", True),),others = False)
        self.process_subelements((
            ("background", "background", None,       False, False),
            ("comment",    "comment",    None,       False, False),
            ("test",       "tests",      Ftest,      False, True),
            ("testgroup",  "testgroups", Ftestgroup, False, True)),
            offspec = False)

        # Merge any sub-testgroups into tests
        if self.testgroups != [] :
            tests = []
            tg = list(self.testgroups) # Want to preserve original list
            for elem in self.element :
                if elem.tag == "test":
                    tests.append(self.tests.pop(0))
                elif elem.tag == "testgroup" :
                    tests.append(tg.pop(0))
            self.tests = tests

class Ftest(ETU.ETelement) :
    def __init__(self, element) :
        super(Ftest,self).__init__(element)
        self.process_subelements((
            ("stylename", "stylename",   None,       False, False),
            ("background", "background", None,       False, False),
            ("rtl",        "rtl",        None,       False, False),
            ("comment",    "comment",    None,       False, False),
            ("string",     "string",     Fstring,    True,  False)),
            offspec = False)

class Fstring(ETU.ETelement) :
    def __init__(self, element) :
        super(Fstring,self).__init__(element)


def getattrib(element,attrib) :
    return element.attrib[attrib] if attrib in element.attrib else None

