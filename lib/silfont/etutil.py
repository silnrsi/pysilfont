#!/usr/bin/env python
from __future__ import unicode_literals
'Classes and functions for handling XML files in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

try:
    str = unicode
    chr = unichr
except NameError: # Will  occur with Python 3
    pass
from xml.etree import ElementTree as ET
import silfont.core

import re, os, codecs, io, collections

_elementprotect = {
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;' # Copy of element protect with double quote added

class ETWriter(object) :
    """ General purpose ElementTree pretty printer complete with options for attribute order
        beyond simple sorting, and which elements should use cdata

        Note there is no support for namespaces.  Originally there was, and if it is needed in the future look at
        commits from 10th May 2018 or earlier.  The code there would need reworking!"""

    def __init__(self, etree, attributeOrder = {}, takesCData = set(),
            indentIncr = "  ", indentFirst = "  ", indentML = False, inlineelem=[], precision = None, floatAttribs = [], intAttribs = []):
        self.root = etree
        self.attributeOrder = attributeOrder    # Sort order for attributes - just one list for all elements
        self.takesCData = takesCData
        self.indentIncr = indentIncr            # Incremental increase in indent
        self.indentFirst = indentFirst          # Indent for first level
        self.indentML = indentML                # Add indent to multi-line strings
        self.inlineelem = inlineelem            # For supporting in-line elements.  Does not work with mix of inline and other subelements in same element
        self.precision = precision              # Precision to use outputting numeric attribute values
        self.floatAttribs = floatAttribs        # List of float/real attributes used with precision
        self.intAttribs = intAttribs

    def _protect(self, txt, base=_attribprotect) :
        return re.sub(r'['+r"".join(base.keys())+r"]", lambda m: base[m.group(0)], txt)

    def serialize_xml(self, base = None, indent = '') :
        # Create the xml and return as a string
        outstrings = []
        outstr=""
        if base is None :
            base = self.root
            outstr += '<?xml version="1.0" encoding="UTF-8"?>\n'
            if '.pi' in base.attrib : # Processing instructions
                for pi in base.attrib['.pi'].split(",") : outstr += '<?{}?>\n'.format(pi)

            if '.doctype' in base.attrib : outstr += '<!DOCTYPE {}>\n'.format(base.attrib['.doctype'])

        tag = base.tag
        attribs = base.attrib

        if '.comments' in attribs :
            for c in attribs['.comments'].split(",") : outstr += '{}<!--{}-->\n'.format(indent, c)

        i = indent if tag not in self.inlineelem else ""
        outstr += '{}<{}'.format(i, tag)

        for k in sorted(list(attribs.keys()), key=lambda x: self.attributeOrder.get(x, x)):
            if k[0] != '.' :
                att = attribs[k]
                if self.precision is not None and k in self.floatAttribs :
                    if "." in att:
                        num = round(float(att), self.precision)
                        att = int(num) if num == int(num) else num
                elif k in self.intAttribs :
                        att = int(round(float(att)))
                else:
                    att = self._protect(att)
                outstr += ' {}="{}"'.format(k, att)

        if len(base) or (base.text and base.text.strip()) :
            outstr += '>'
            if base.text and base.text.strip() :
                if tag not in self.takesCData :
                    t = base.text
                    if self.indentML : t = t.replace('\n', '\n' + indent)
                    t = self._protect(t, base=_elementprotect)
                else :
                    t = "<![CDATA[\n\t" + indent + base.text.replace('\n', '\n\t' + indent) + "\n" + indent + "]]>"
                outstr += t
            if len(base) :
                if base[0].tag not in self.inlineelem : outstr += '\n'
                if base == self.root:
                    incr = self.indentFirst
                else:
                    incr = self.indentIncr
                outstrings.append(outstr); outstr=""
                for b in base : outstrings.append(self.serialize_xml(base=b, indent=indent + incr))
                if base[-1].tag not in self.inlineelem : outstr += indent
            outstr += '</{}>'.format(tag)
        else :
            outstr += '/>'
        if base.tail and base.tail.strip() :
            outstr += self._protect(base.tail, base=_elementprotect)
        if tag not in self.inlineelem : outstr += "\n"

        if '.commentsafter' in base.attrib :
            for c in base.attrib['.commentsafter'].split(",") : outstr += '{}<!--{}-->\n'.format(indent, c)

        outstrings.append(outstr)
        return "".join(outstrings)

class _container(object) :
    # Parent class for other objects
    def __init_(self) :
        self._contents = {}
    # Define methods so it acts like an imutable container
    # (changes should be made via object functions etc)
    def __len__(self):
        return len(self._contents)
    def __getitem__(self, key):
        return self._contents[key]
    def __iter__(self):
        return iter(self._contents)
    def keys(self) :
        return self._contents.keys()

class xmlitem(_container):
    """ The xml data item for an xml file"""

    def __init__(self, dirn = None, filen = None, parse = True, logger=None) :
        self.logger = logger if logger else silfont.core.loggerobj()
        self._contents = {}
        self.dirn = dirn
        self.filen = filen
        self.inxmlstr = ""
        self.outxmlstr = ""
        self.etree = None
        self.type = None
        if filen and dirn :
            fulln = os.path.join( dirn, filen)
            self.inxmlstr = io.open(fulln, "rt", encoding="utf-8").read()
            if parse :
                try:
                    self.etree = ET.fromstring(self.inxmlstr)
                except:
                    try:
                        self.etree = ET.fromstring(self.inxmlstr.encode("utf-8"))
                    except Exception as e:
                        self.logger.log("Failed to parse xml for " + fulln, "E")
                        self.logger.log(str(e), "S")

    def write_to_file(self,dirn,filen) :
        outfile = io.open(os.path.join(dirn,filen),'w', encoding="utf-8")
        outfile.write(self.outxmlstr)

class ETelement(_container):
    # Class for an etree element. Mainly used as a parent class
    # For each tag in the element, ETelement[tag] returns a list of sub-elements with that tag
    # process_subelements can set attributes for each tag based on a supplied spec
    def __init__(self,element) :
        self.element = element
        self._contents = {}
        self.reindex()

    def reindex(self) :
        self._contents = collections.defaultdict(list)
        for e in self.element :
            self._contents[e.tag].append(e)

    def remove(self,subelement) :
        self._contents[subelement.tag].remove(subelement)
        self.element.remove(subelement)

    def append(self,subelement) :
        self._contents[subelement.tag].append(subelement)
        self.element.append(subelement)

    def insert(self,index,subelement) :
        self._contents[subelement.tag].insert(index,subelement)
        self.element.insert(index,subelement)

    def replace(self,index,subelement) :
        self._contents[subelement.tag][index] = subelement
        self.element[index] = subelement

    def process_attributes(self, attrspec, others = False) :
        # Process attributes based on list of attributes in the format:
        #   (element attr name, object attr name, required)
        # If attr does not exist and is not required, set to None
        # If others is True, attributes not in the list are allowed
        # Attributes should be listed in the order they should be output if writing xml out

        if not hasattr(self,"parseerrors") or self.parseerrors is None: self.parseerrors=[]

        speclist = {}
        for (i,spec) in enumerate(attrspec) : speclist[spec[0]] = attrspec[i]

        for eaname in speclist :
            (eaname,oaname,req) = speclist[eaname]
            setattr(self, oaname, getattrib(self.element,eaname))
            if req and getattr(self, oaname) is None : self.parseerrors.append("Required attribute " + eaname + " missing")

        # check for any other attributes
        for att in self.element.attrib :
            if att not in speclist :
                if others:
                    setattr(self, att, getattrib(self.element,att))
                else :
                    self.parseerrors.append("Invalid attribute " + att)

    def process_subelements(self,subspec, offspec = False) :
        # Process all subelements based on spec of expected elements
        # subspec is a list of elements, with each list in the format:
        #    (element name, attribute name, class name, required, multiple valeus allowed)
        # If cl is set, attribute is set to an object made with that class; otherwise just text of the element

        if not hasattr(self,"parseerrors")  or self.parseerrors is None : self.parseerrors=[]

        def make_obj(self,cl,element) : # Create object from element and cascade parse errors down
            if cl is None : return element.text
            if cl is ETelement :
                obj = cl(element) # ETelement does not require parent object, ie self
            else :
                obj = cl(self,element)
            if hasattr(obj,"parseerrors") and obj.parseerrors != [] :
                if hasattr(obj,"name") and obj.name is not None : # Try to find a name for error reporting
                    name = obj.name
                elif hasattr(obj,"label") and obj.label is not None  :
                    name = obj.label
                else :
                    name = ""

                self.parseerrors.append("Errors parsing " + element.tag + " element: " + name)
                for error in obj.parseerrors :
                    self.parseerrors.append("  " + error)
            return obj

        speclist = {}
        for (i,spec) in enumerate(subspec) : speclist[spec[0]] = subspec[i]

        for ename in speclist :
            (ename,aname,cl,req,multi) = speclist[ename]
            initval = [] if multi else None
            setattr(self,aname,initval)

        for ename in self : # Process all elements
            if ename in speclist :
                (ename,aname,cl,req,multi) = speclist[ename]
                elements = self[ename]
                if multi :
                    for elem in elements : getattr(self,aname).append(make_obj(self,cl,elem))
                else :
                    setattr(self,aname,make_obj(self,cl,elements[0]))
                    if len(elements) > 1 : self.parseerrors.append("Multiple " + ename + " elements not allowed")
            else:
                if offspec: # Elements not in spec are allowed so create list of sub-elemente.
                    setattr(self,ename,[])
                    for elem in elements : getattr(self,ename).append(ETelement(elem))
                else :
                    self.parseerrors.append("Invalid element: " + ename)

        for ename in speclist : # Check values exist for required elements etc
            (ename,aname,cl,req,multi) = speclist[ename]

            val = getattr(self,aname)
            if req :
                if multi and val == [] : self.parseerrors.append("No " + ename + " elements ")
                if not multi and val == None : self.parseerrors.append("No " + ename + " element")

def makeAttribOrder(attriblist) : # Turn a list of attrib names into an attributeOrder dict for ETWriter
        return dict(map(lambda x:(x[1], x[0]), enumerate(attriblist)))

def getattrib(element,attrib) : return element.attrib[attrib] if attrib in element.attrib else None