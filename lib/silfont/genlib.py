#!/usr/bin/env python
'UFO handling script under development'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET
import re, sys, os, codecs

_elementprotect = {
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;'

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

    def _protect(self, txt, base=_attribprotect) :
        return re.sub(ur'['+ur"".join(base.keys())+ur"]", lambda m: base[m.group(0)], txt)

    def _nsprotectattribs(self, attribs, localattribs, namespaces) :
        if attribs is not None :
            for k, v in attribs.items() :
                (lt, lq, lns) = self._localisens(k)
                if lns and lns not in namespaces :
                    namespaces[lns] = lq
                    localattribs['xmlns:'+lq] = lns
                localattribs[lt] = v

    def serialize_xml(self, write, base = None, indent = '', topns = True, namespaces = {}) :
        """Output the object using write() in a normalised way:
                topns if set puts all namespaces in root element else put them as low as possible"""
        if base is None :
            base = self.root
            write('<?xml version="1.0" encoding="UTF-8"?>\n')
            doctype=getattr(base, "doctype", "")
            if doctype <> "":
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
        
        for c in getattr(base, 'comments', []) :
            write(u'{}<!--{}-->\n'.format(indent, c))
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
                incr = self.indentFirst 
                self.indentFirst = self.indentIncr
                self.serialize_xml(write, base=b, indent=indent + incr, topns=topns, namespaces=namespaces.copy())
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
        for c in getattr(base, 'commentsafter', []) :
            write(u'{}<!--{}-->\n'.format(indent, c))

    def add_namespace(self, q, ns) :
        if ns in self.namespaces : return self.namespaces[ns]
        self.namespaces[ns] = q
        return q

class dirTree(dict) :
    """ An object to hold list of all files and directories in a directory
        with option to read sub-directory contents into dirTree objects.
        Iterates through readSub levels of subfolders """
    def __init__(self,dirn,readSub = 3) :
        for name in os.listdir(dirn) :
            item={}
            if os.path.isdir(os.path.join(dirn, name)) :
                item["type"] = "d"
                if readSub :
                    item["tree"] = dirTree(os.path.join(dirn,name),readSub-1)
            else :
                item["type"] = "f"
            self[name] = item
        
    def subTree(self,path) : # Returns dirTree object for a subtree based on subfolder name(s)
        # 'path' can be supplied as either a relative path (eg "subf/subsubf") or array (eg ['subf','subsubf']
        if type(path) is str : path = self._split(path)
        subf=path[0]
        if subf in self:
            if 'tree' in self[subf] :
                tree = self[subf]['tree']
            else :
                tree = ""
        else : return ""
        
        if len(path) == 1 :
            return tree
        else :
            path.pop(0)
            return tree.subTree(path)
        
    def _split(self,path) : # Turn a relative path into an array of subfolders
        npath = [os.path.split(path)[1]]
        while os.path.split(path)[0] :
            path = os.path.split(path)[0]
            npath.insert(0,os.path.split(path)[1])
        return npath

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
                sys.exit()
            for line in inxml.readlines() :
                self.inxmlstr = self.inxmlstr + line
            if parse :
                self.etree = ET.fromstring(self.inxmlstr)

    def write_to_xml(self,text) : # Used by ETWriter.serializeXML
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
    