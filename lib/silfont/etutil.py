#!/usr/bin/env python
'Classes and functions for handling XML files in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from xml.etree import cElementTree as ET
from glob import glob
import silfont.core

import re, sys, os, codecs, argparse, datetime, shutil, csv, collections

_elementprotect = {
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;' # Copy of element protect with double quote added

class ETWriter(object) :
    """ General purpose ElementTree pretty printer complete with options for attribute order
        beyond simple sorting, and which elements should use cdata """

    def __init__(self, etree, namespaces = None, attributeOrder = {}, takesCData = set(), indentIncr = "  ", indentFirst = "  ", indentML = False, inlineelem=[]):
        self.root = etree
        if namespaces is None : namespaces = {}
        self.namespaces = namespaces
        self.attributeOrder = attributeOrder    # Sort order for attributes - just one list for all elements
        self.takesCData = takesCData
        self.indentIncr = indentIncr            # Incremental increase in indent
        self.indentFirst = indentFirst          # Indent for first level
        self.indentML = indentML                # Add indent to multi-line strings
        self.inlineelem = inlineelem            # For supporting in-line elements.  Does not work with mix of inline and other subelements in same element

    def _protect(self, txt, base=_attribprotect) :
        return re.sub(ur'['+ur"".join(base.keys())+ur"]", lambda m: base[m.group(0)], txt)

    def serialize_xml(self, write, base = None, indent = '') :
        """Output the object using write() in a normalised way:
                If namespaces are used, use serialize_nsxml instead"""
        outstr=""

        if base is None :
            base = self.root
            outstr += '<?xml version="1.0" encoding="UTF-8"?>\n'
            if '.pi' in base.attrib : # Processing instructions
                for pi in base.attrib['.pi'].split(",") : outstr += u'<?{}?>\n'.format(pi)

            if '.doctype' in base.attrib : outstr += u'<!DOCTYPE {}>\n'.format(base.attrib['.doctype'])

        tag = base.tag
        attribs = base.attrib

        if '.comments' in attribs :
            for c in attribs['.comments'].split(",") : outstr += u'{}<!--{}-->\n'.format(indent, c)

        i = indent if tag not in self.inlineelem else ""
        outstr += u'{}<{}'.format(i, tag)

        for k in sorted(attribs.keys(), cmp=lambda x,y: cmp(self.attributeOrder.get(x, 999), self.attributeOrder.get(y, 999)) or cmp(x, y)) :
            if k[0] <> '.' : outstr += u' {}="{}"'.format(k, attribs[k])
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
                write(outstr); outstr=""
                for b in base : self.serialize_xml(write, base=b, indent=indent + incr)
                if base[-1].tag not in self.inlineelem : outstr += indent
            outstr += '</{}>'.format(tag)
        else :
            outstr += '/>'
        if base.tail and base.tail.strip() :
            outstr += self._protect(base.tail, base=_elementprotect)
        if tag not in self.inlineelem : outstr += "\n"

        if '.commentsafter' in base.attrib :
            for c in base.attrib['.commentsafter'].split(",") : outstr += u'{}<!--{}-->\n'.format(indent, c)

        write(outstr)

    def _localisens(self, tag) :
        if tag[0] == '{' :
            ns, localname = tag[1:].split('}', 1)
            qname = self.namespaces.get(ns, '')
            if qname :
                return ('{}:{}'.format(qname, localname), qname, ns)
            else :
                self.nscount += 1
                return (localname, 'ns_' + str(self.nscount), ns)
        else :
            return (tag, None, None)

    def _nsprotectattribs(self, attribs, localattribs, namespaces) :
        if attribs is not None :
            for k, v in attribs.items() :
                (lt, lq, lns) = self._localisens(k)
                if lns and lns not in namespaces :
                    namespaces[lns] = lq
                    localattribs['xmlns:'+lq] = lns
                localattribs[lt] = v

    def serialize_nsxml(self, write, base = None, indent = '', topns = True, namespaces = {}) :
        ## Not currently used.  Needs amending to mirror changes in serialize_xml for dummy attributes (and efficiency)"""
        """Output the object using write() in a normalised way:
                topns if set puts all namespaces in root element else put them as low as possible"""
        if base is None :
            base = self.root
            write('<?xml version="1.0" encoding="UTF-8"?>\n')
            doctype = base.attrib['_doctype'] if '_doctype' in base.attrib else None
            if doctype is not None:
                del base.attrib["_doctype"]
                write(u'<!DOCTYPE {}>\n'.format(doctype))
        (tag, q, ns) = self._localisens(base.tag)

        localattribs = {}
        if ns and ns not in namespaces :
            namespaces[ns] = q
            localattribs['xmlns:'+q] = ns
        if topns :
            if base == self.root :
                for n,q in self.namespaces.items() :
                    localattribs['xmlns:'+q] = n
                    namespaces[n] = q
        else :
            for c in base :
                (lt, lq, lns) = self._localisens(c.tag)
                if lns and lns not in namespaces :
                    namespaces[lns] = q
                    localattribs['xmlns:'+lq] = lns
        self._nsprotectattribs(getattr(base, 'attrib', None), localattribs, namespaces)

        if '_comments' in base.attrib :
            for c in base.attrib['_comments'].split(",") :
               write(u'{}<!--{}-->\n'.format(indent, c))
            del base.attrib["_comments"]

        write(u'{}<{}'.format(indent, tag))
        if len(localattribs) :
            maxAts = len(self.attributeOrder) + 1
            def cmpattrib(x, y) :
                return cmp(self.attributeOrder.get(x, maxAts), self.attributeOrder.get(y, maxAts)) or cmp(x, y)
            for k in sorted(localattribs.keys(), cmp=cmpattrib) :
                write(u' {}="{}"'.format(self._localisens(k)[0], self._protect(localattribs[k])))
        if len(base) :
            write('>\n')
            for b in base :
                if base == self.root:
                    incr = self.indentFirst
                else:
                    incr = self.indentIncr
                self.serialize_nsxml(write, base=b, indent=indent + incr, topns=topns, namespaces=namespaces.copy())
            write('{}</{}>\n'.format(indent, tag))
        elif base.text :
            if base.text.strip() :
                if tag not in self.takesCData :
                    t = base.text

                    if self.indentML : t = t.replace('\n', '\n' + indent)
                    t = self._protect(t, base=_elementprotect)
                else :
                    t = "<![CDATA[\n\t" + indent + base.text.replace('\n', '\n\t' + indent) + "\n" + indent + "]]>"
                write(u'>{}</{}>\n'.format(t, tag))
            else :
                write('/>\n')
        else :
            write('/>\n')

        if '_commentsafter' in base.attrib :
            for c in base.attrib['_commentsafter'].split(",") :
               write(u'{}<!--{}-->\n'.format(indent, c))
            del base.attrib["_commentsafter"]

    def add_namespace(self, q, ns) :
        if ns in self.namespaces : return self.namespaces[ns]
        self.namespaces[ns] = q
        return q

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

class xmlitem(_container) :
    """ The xml data item for an xml file"""

    def __init__(self, dirn = None, filen = None, parse = True ) :
        self._contents = {}
        self.dirn = dirn
        self.filen = filen
        self.inxmlstr = ""
        self.outxmlstr = ""
        self.etree = None
        self.type = None
        if filen and dirn :
            try :
                inxml=open(os.path.join( dirn, filen), "r")
            except Exception as e :
                print e
                sys.exit(1)
            for line in inxml.readlines() :
                self.inxmlstr = self.inxmlstr + line
            inxml.close()
            if parse :
                self.etree = ET.fromstring(self.inxmlstr)

    def write_to_xml(self,text) : # Used by ETWriter.serialize_xml()
        self.outxmlstr = self.outxmlstr + text

    def write_to_file(self,dirn,filen) :
        outfile=codecs.open(os.path.join(dirn,filen),'w','utf-8')
        outfile.write(self.outxmlstr)
        outfile.close

class ETelement(_container) :
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