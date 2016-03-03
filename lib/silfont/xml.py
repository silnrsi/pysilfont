#!/usr/bin/env python
'Classes and functions for handling XML files in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '1.0.0'

from xml.etree import cElementTree as ET
from glob import glob
import re, sys, os, codecs, argparse, datetime, shutil, csv

_elementprotect = {
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;' # Copy of element protect with double quote added

class ETWriter(object) :
    """ General purpose ElementTree pretty printer complete with options for attribute order
        beyond simple sorting, and which elements should use cdata """

    def __init__(self, etree, namespaces = None, attributeOrder = {}, takesCData = set(), indentIncr = "  ", indentFirst = "  ", indentML = False):
        self.root = etree
        if namespaces is None : namespaces = {}
        self.namespaces = namespaces
        self.attributeOrder = attributeOrder    # Sort order for attributes - just one list for all elements
        self.takesCData = takesCData
        self.indentIncr = indentIncr            # Incremental increase in indent
        self.indentFirst = indentFirst          # Indent for first level
        self.indentML = indentML                # Add indent to multi-line strings

    def _protect(self, txt, base=_attribprotect) :
        return re.sub(ur'['+ur"".join(base.keys())+ur"]", lambda m: base[m.group(0)], txt)

    def serialize_xml(self, write, base = None, indent = '') :
        """Output the object using write() in a normalised way:
                If namespaces are used, use serialize_nsxml instead"""
        outstr=""

        if base is None :
            base = self.root
            outstr += '<?xml version="1.0" encoding="UTF-8"?>\n'
            if '.doctype' in base.attrib : outstr += u'<!DOCTYPE {}>\n'.format(base.attrib['.doctype'])

        tag = base.tag
        attribs = base.attrib

        if '.comments' in attribs :
            for c in attribs['.comments'].split(",") : outstr += u'{}<!--{}-->\n'.format(indent, c)

        outstr += u'{}<{}'.format(indent, tag)

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
                outstr += '\n'
                if base == self.root:
                    incr = self.indentFirst
                else:
                    incr = self.indentIncr
                write(outstr); outstr=""
                for b in base : self.serialize_xml(write, base=b, indent=indent + incr)
                outstr += indent
            outstr += '</{}>'.format(tag)
        else :
            outstr += '/>'
        if base.tail and base.tail.strip() :
            outstr += self._protect(base.tail, base=_elementprotect)
        outstr += "\n"

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

class xmlitem(object) :
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

    # Define methods so it acts like an imumtable container -
    # changes should be made via object methods
    def __len__(self):
        return len(self._contents)
    def __getitem__(self, key):
        return self._contents[key]
    def __iter__(self):
        return iter(self._contents)
    def keys(self) :
        return self._contents.keys()

def makeAttribOrder(attriblist) : # Turn a list of attrib names into an attributeOrder dict for ETWriter
        return dict(map(lambda x:(x[1], x[0]), enumerate(attriblist)))
