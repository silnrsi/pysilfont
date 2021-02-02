#!/usr/bin/env python
'Classes and functions for use handling FTML objects in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from xml.etree import ElementTree as ET
from fontTools import ttLib
import re
from xml.sax.saxutils import quoteattr
import silfont.core
import silfont.etutil as ETU

# Regular expression for parsing font name
fontspec =          re.compile(r"""^        # beginning of string
                    (?P<rest>[A-Za-z ]+?)   # Font Family Name
                    \s*(?P<bold>Bold)?      # Bold
                    \s*(?P<italic>Italic)?  # Italic
                    \s*(?P<regular>Regular)? # Regular
                    $""", re.VERBOSE)       # end of string

class Fxml(ETU.ETelement) :
    def __init__(self, file = None, xmlstring = None, testgrouplabel = None, logger = None, params = None) :
        self.logger = logger if logger is not None else silfont.core.loggerobj()
        self.params = params if params is not None else silfont.core.parameters()
        self.parseerrors=None
        if not exactlyoneof(file, xmlstring, testgrouplabel) : self.logger.log("Must supply exactly one of file, xmlstring and testgrouplabel","X")

        if testgrouplabel : # Create minimal valid ftml
            xmlstring = '<ftml version="1.0"><head></head><testgroup label=' + quoteattr(testgrouplabel) +'></testgroup></ftml>'

        if file and not hasattr(file, 'read') : self.logger.log("'file' is not a file object", "X") # ET.parse would also work on file name, but other code assumes file object

        try :
            if file :
                self.element = ET.parse(file).getroot()
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

        self.stylesheet = {}
        if file : # If reading from file, look to see if a stylesheet is present in xml processing instructions
            file.seek(0) # Have to re-read file since ElementTree does not support processing instructions
            for line in file :
                if line[0:2] == "<?" :
                    line = line.strip()[:-2] # Strip white space and removing training ?>
                    parts = line.split(" ")
                    if parts[0] == "<?xml-stylesheet" :
                        for part in parts[1:] :
                            (name,value) = part.split("=")
                            self.stylesheet[name] = value[1:-1] # Strip quotes
                        break
                else :
                    break

        self.filename = file if file else None

        if self.parseerrors:
            self.logger.log("Errors parsing ftml element:","E")
            for error in self.parseerrors : self.logger.log("  " + error,"E")
            self.logger.log("Invalid FTML", "S")

    def save(self, file) :
        self.outxmlstr=""
        element = self.create_element()
        etw = ETU.ETWriter(element, inlineelem = ["em"])
        self.outxmlstr = etw.serialize_xml()
        file.write(self.outxmlstr)

    def create_element(self) : # Create a new Elementtree element based on current object contents
        element = ET.Element('ftml', version = str(self.version))
        if self.stylesheet : # Create dummy .pi attribute for style sheet processing instruction
            pi = "xml-stylesheet"
            for attrib in sorted(self.stylesheet) : pi = pi + ' ' + attrib + '="' + self.stylesheet[attrib] + '"' ## Spec is not clear about what order attributes should be in
            element.attrib['.pi'] = pi
        element.append(self.head.create_element())
        for testgroup in self.testgroups : element.append(testgroup.create_element())
        return element

class Fhead(ETU.ETelement) :
    def __init__(self, parent, element) :
        self.parent = parent
        self.logger = parent.logger
        super(Fhead,self).__init__(element)

        self.process_subelements((
            ("comment",    "comment",    None,          False, False),
            ("fontscale",  "fontscale",  None,          False, False),
            ("fontsrc",    "fontsrc",    Ffontsrc,      False, True),
            ("styles",     "styles",     ETU.ETelement, False, False ), # Initially just basic elements; Fstyles created below
            ("title",      "title",      None,          False, False),
            ("widths",     "widths",     _Fwidth,       False, False)),
            offspec = True)

        if self.fontscale is not None : self.fontscale = int(self.fontscale)
        if self.styles is not None :
            styles = {}
            for styleelem in self.styles["style"] :
                style = Fstyle(self, element = styleelem)
                styles[style.name] = style
                if style.parseerrors:
                    name = "" if style.name is None else style.name
                    self.parseerrors.append("Errors parsing style element: " + name)
                    for error in style.parseerrors : self.parseerrors.append("  " + error)
            self.styles = styles
        if self.widths is not None : self.widths = self.widths.widthsdict # Convert _Fwidths object into dict

        self.elements = dict(self._contents) # Dictionary of all elements, particularly for handling non-standard elements

    def findstyle(self, name = None, feats = None, lang = None) :
        if self.styles is not None:
            for s in self.styles :
                style = self.styles[s]
                if style.feats == feats and style.lang == lang :
                    if name is None or name == style.name : return style # if name is supplied it must match
        return None

    def addstyle(self, name, feats = None, lang = None) : # Return style if it exists otherwaise create new style with newname
        s = self.findstyle(name, feats, lang)
        if s is None :
            if self.styles is None:
                self.styles = {}
            if name in self.styles : self.logger.log("Adding duplicate style name " + name, "X")
            s = Fstyle(self, name = name, feats = feats, lang = lang)
            self.styles[name] = s
        return s

    def create_element(self) :
        element = ET.Element('head')
        # Add in-spec sub-elements in alphabetic order
        if self.comment   : x = ET.SubElement(element, 'comment') ; x.text = self.comment
        if self.fontscale : x = ET.SubElement(element, 'fontscale') ; x.text = str(self.fontscale)
        if isinstance(self.fontsrc, list):
            # Allow multiple fontsrc
            for fontsrc in self.fontsrc:
                element.append(fontsrc.create_element())
        elif self.fontsrc is not None:
            element.append(self.fontsrc.create_element())
        if self.styles :
            x = ET.SubElement(element, 'styles')
            for style in sorted(self.styles) : x.append(self.styles[style].create_element())
        if self.title     : y = ET.SubElement(element, 'title') ; y.text = self.title
        if not self.widths is None :
            x = ET.SubElement(element, 'widths')
            for width in sorted(self.widths) :
                if self.widths[width] is not None: x.set(width, self.widths[width])

        # Add any non-spec elements
        for el in sorted(self.elements) :
            if el not in ("comment", "fontscale", "fontsrc", "styles", "title", "widths") :
                for elem in self.elements[el] : element.append(elem)

        return element

class Ffontsrc(ETU.ETelement) :
    # This library only supports a single font in the fontsrc as recommended by the FTML spec
    # Currently it only supports simple url() and local() values

    def __init__(self, parent, element = None, text = None, label=None) :
        self.parent = parent
        self.logger = parent.logger
        self.parseerrors = []

        if not exactlyoneof(element, text) : self.logger.log("Must supply exactly one of element and text","X")

        try:
            (txt, url, local) = parsefontsrc(text, allowplain=True) if text else parsefontsrc(element.text)
        except ValueError as e :
            txt = text if text else element.text
            self.parseerrors.append(str(e) + ": " + txt)
        else :
            if text : element = ET.Element("fontsrc") ; element.text = txt
            if label : element.set('label', label)
            super(Ffontsrc,self).__init__(element)
            self.process_attributes((
                ("label", "label", False),),
                others=False)
            self.text = txt
            self.url = url
            self.local = local
            if self.local : # Parse font name to find if bold, italic etc
                results = re.match(fontspec, self.local) ## Does not cope with -, eg Gentium-Bold. Should it?"
                self.fontfamily = results.group('rest')
                self.bold = results.group('bold') != None
                self.italic = results.group('italic') != None
            else :
                self.fontfamily = None # If details are needed call getweights()

    def addfontinfo(self) : # set fontfamily, bold and italic by looking inside font
        (ff, bold, italic) = getfontinfo(self.url)
        self.fontfamily = ff
        self.bold = bold
        self.italic = italic

    def create_element(self) :
        element = ET.Element("fontsrc")
        element.text = self.text
        if self.label  : element.set("label", self.label)
        return element

class Fstyle(ETU.ETelement) :
    def __init__(self, parent, element = None, name = None, feats = None, lang = None) :
        self.parent = parent
        self.logger = parent.logger
        if element is not None :
            if name or feats or lang : parent.logger("Can't supply element and other parameters", "X")
        else :
            if name is None : self.logger.log("Must supply element or name to Fstyle", "X")
            element = self.element = ET.Element("style", name = name)
            if feats is not None :
                if type(feats) is dict : feats = self.dict_to_string(feats)
                element.set('feats',feats)
            if lang is not None : element.set('lang', lang)
        super(Fstyle,self).__init__(element)

        self.process_attributes((
            ("feats", "feats", False),
            ("lang",  "lang",  False),
            ("name",  "name",  True)),
            others = False)

        if type(self.feats) is str : self.feats = self.string_to_dict(self.feats)

    def string_to_dict(self, string) : # Split string on ',', then add to dict splitting on " " and removing quotes
        dict={}
        for f in string.split(','):
            f = f.strip()
            m = re.match(r'''(?P<quote>['"])(\w{4})(?P=quote)\s+(\d+|on|off)$''', f)
            if m:
                dict[m.group(2)] = m.group(3)
            else:
                self.logger.log(f'Invalid feature syntax "{f}"', 'E')
        return dict

    def dict_to_string(self, dict) :
        str=""
        for name in sorted(dict) :
            if dict[name] is not None : str += "'" + name + "' " + dict[name] + ", "
        str = str[0:-2] # remove final ", "
        return str

    def create_element(self) :
        element = ET.Element("style", name = self.name)
        if self.feats : element.set("feats", self.dict_to_string(self.feats))
        if self.lang  : element.set("lang", self.lang)
        return element


class _Fwidth(ETU.ETelement) : # Only used temporarily whilst parsing xml
    def __init__(self, parent, element) :
        super(_Fwidth,self).__init__(element)
        self.parent = parent
        self.logger = parent.logger

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
    def __init__(self, parent, element = None, label = None) :
        self.parent = parent
        self.logger = parent.logger
        if not exactlyoneof(element, label) : self.logger.log("Must supply exactly one of element and label","X")

        if label : element = ET.Element("testgroup", label = label)

        super(Ftestgroup,self).__init__(element)

        self.subgroup = True if type(parent) is Ftestgroup else False
        self.process_attributes((
            ("background", "background", False),
            ("label",      "label",      True)),
            others = False)
        self.process_subelements((
            ("comment",    "comment",    None,       False, False),
            ("test",       "tests",      Ftest,      False, True),
            ("testgroup",  "testgroups", Ftestgroup, False, True)),
            offspec = False)
        if self.subgroup and self.testgroups != [] : parent.parseerrors.append("Only one level of testgroup nesting permitted")

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

    def create_element(self) :
        element = ET.Element("testgroup")
        if self.background : element.set("background", self.background)
        element.set("label", self.label)
        if self.comment : x = ET.SubElement(element, 'comment') ; x.text = self.comment
        for test in self.tests : element.append(test.create_element())
        return element

class Ftest(ETU.ETelement) :
    def __init__(self, parent, element = None, label = None, string = None) :
        self.parent = parent
        self.logger = parent.logger
        if not exactlyoneof(element, (label, string)) : self.logger.log("Must supply exactly one of element and label/string","X")

        if label :
            element = ET.Element("test", label = label)
            x = ET.SubElement(element,"string") ; x.text = string

        super(Ftest,self).__init__(element)

        self.process_attributes((
            ("background", "background", False),
            ("label",      "label",      True),
            ("rtl",        "rtl",        False),
            ("stylename",  "stylename",  False)),
            others = False)

        self.process_subelements((
            ("comment",    "comment",    None,       False, False),
            ("string",     "string",     _Fstring,    True,  False)),
            offspec = False)

        self.string = self.string.string # self.string initially a temporary _Fstring element

    def str(self, noems = False) : # Return formatted version of string
        string = self.string
        if noems :
            string = string.replace("<em>","")
            string = string.replace("</em>","")
        return string ## Other formatting options to be added as needed cf ftml2odt

    def create_element(self) :
        element = ET.Element("test")
        if self.background : element.set("background", self.background)
        element.set("label", self.label)
        if self.rtl :        element.set("rtl",        self.rtl)
        if self.stylename :  element.set("stylename",  self.stylename)
        if self.comment : x = ET.SubElement(element, "comment") ; x.text = self.comment
        x = ET.SubElement(element, "string") ; x.text = self.string

        return element

class _Fstring(ETU.ETelement) : # Only used temporarily whilst parsing xml
    def __init__(self, parent, element = None) :
        self.parent = parent
        self.logger = parent.logger
        super(_Fstring,self).__init__(element)
        self.process_subelements((("em", "em", ETU.ETelement,False, True),), offspec = False)
        # Need to build text of string to include <em> subelements
        self.string = element.text if element.text else ""
        for em in self.em :
            self.string += "<em>{}</em>{}".format(em.element.text, em.element.tail)

def getattrib(element,attrib) :
    return element.attrib[attrib] if attrib in element.attrib else None

def exactlyoneof( *args ) : # Check one and only one of args is not None

    last = args[-1]           # Check if last argument is a tuple - in which case
    if type(last) is tuple :  # either all or none of list must be None
        for test in last[1:] :
            if (test is None) != (last[0] == None) : return False
        args = list(args)  # Convert to list so last val can be changed
        args[-1] = last[0] # Now valid to test on any item in tuple

    one = False
    for test in args :
        if test is not None :
            if one : return False # already have found one not None
            one = True
    if one : return True
    return False

def parsefontsrc(text, allowplain = False) : # Check fontsrc text is valid and return normalised text, url and local values
    ''' - if multiple (fallback) fonts are specified, just process the first one
        - just handles simple url() or local() formats
        - if allowplain is set, allows text without url() or local() and decides which based on "." in text '''
    text = text.split(",")[0] # If multiple (fallback) fonts are specified, just process the first one
    #if allowplain and not re.match(r"^(url|local)[(][^)]+[)]",text) : # Allow for text without url() or local() form
    if allowplain and not "(" in text : # Allow for text without url() or local() form
        plain = True
        if "." in text :
            type = "url"
        else :
            type = "local"
    else :
        type = text.split("(")[0]
        if type == "url" :
            text = text.split("(")[1][:-1].strip()
        elif type == "local" :
            text = text.split("(")[1][:-1].strip()
        else : raise ValueError("Invalid fontsrc string")
    if type == "url" :
        return ("url("+text+")", text, None)
    else :
        return ("local("+text+")", None , text)

    return (text,url,local)

def getfontinfo(filename) : # peek inside the font for the name, weight, style
        f = ttLib.TTFont(filename)
        # take name from name table, NameID 1, platform ID 3, Encoding ID 1 (possible fallback platformID 1, EncodingID =0)
        n = f['name'] # name table from font
        fontname = n.getName(1,3,1).toUnicode() # nameID 1 = Font Family name
        # take bold and italic info from OS/2 table, fsSelection bits 0 and 5
        o = f['OS/2'] # OS/2 table
        italic = (o.fsSelection & 1) > 0
        bold = (o.fsSelection & 32) > 0
        return (fontname, bold, italic)

