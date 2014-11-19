#!/usr/bin/env python
'UFO handling script under development'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET
from copy import deepcopy
import re, sys, os

_elementprotect = {
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;'

class ETWriter(object) :
    """ General purpose ElementTree pretty printer complete with options for attribute order
        beyond simple sorting, and which elements should use cdata """

    def __init__(self, etree, namespaces = None, attributeOrder = {}, takesCData = set(), indentIncr = "  ", indentFirst = "  "):
        self.root = etree
        if namespaces is None : namespaces = {}
        self.namespaces = namespaces
        self.attributeOrder = attributeOrder
        self.takesCData = takesCData
        self.indentIncr = indentIncr
        self.indentFirst = indentFirst

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
            write('<?xml version="1.0" encoding="utf-8"?>\n')
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
                    t = self._protect(base.text.replace('\n', '\n' + indent), base=_elementprotect)
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
        Does not iterate to lower subdirectories """
    def __init__(self,dirn,readSub = True) :
        for name in os.listdir(dirn) :
            item={}
            if os.path.isdir(os.path.join(dirn, name)) :
                item["type"] = "d"
                if readSub :
                    item["tree"] = dirTree(os.path.join(dirn,name),readSub = False)
            else :
                item["type"] = "f"
            self[name] = item

class xmlitem(dict) :
    """ The xml data item for an xml file from the UFO"""

    def __init__(self, fn = None, parse = True ) :
        self.xmlstring = ""
        self.etree = None
        self.type = None
        if fn :
            try :
                inxml=open(fn,"r")
            except Exception as e :
                print e
                sys.exit()
            for line in inxml.readlines() :
                self.xmlstring = self.xmlstring + line
            if parse :
                self.etree = ET.fromstring(self.xmlstring)

    def write_to_xml(self,text) :
        self.xmlstring = self.xmlstring + text

class Ufont(object) :
    """ Object to hold all the data from a UFO"""
    
    def __init__(self, ufodir = "" ) :
        
        if ufodir:
            self.ufodir = ufodir
            print 'Opening UFO for input: ',ufodir
            if not os.path.isdir(ufodir) :
                print ufodir + " not a directory"
                sys.exit()
            # Read list of files and folders in top 2 levels; anything at lower levels just needs copying
            self.tree=dirTree(ufodir)
            (self.path,base) = os.path.split(ufodir)
            (self.base,self.ext) = os.path.splitext(base)            
            # Read metainfo.plist and identify UFO version
            self.metainfo = self._readPlist("metainfo.plist")
            self.UFOversion = self.metainfo["formatVersion"]
            # Read other top-level plists
            if "fontinfo.plist" in self.tree : self.fontinfo = self._readPlist("fontinfo.plist")
            if "groups.plist" in self.tree : self.groups = self._readPlist("groups.plist")
            if "kerning.plist" in self.tree : self.kerning = self._readPlist("kerning.plist")
            if "lib.plist" in self.tree : self.lib = self._readPlist("lib.plist")
            if self.UFOversion == "2" :
                self.layercontents = Uplist() # Create a dummy layer contents so 2 & 3 can be handled the same
                dummylc = "<plist>\n<array>\n<array>\n<string>public.default</string>\n<string>glyphs</string>\n</array>\n</array>\n</plist>"
                self.layercontents.etree = ET.fromstring(dummylc)
                self.layercontents.populate_dict()
            else :
                self.layercontents = self._readPlist("layercontents.plist")
            # Process the glyphs directories)
            self.layers = []
            for i in sorted(self.layercontents.keys() ) :
                layername = self.layercontents[i][0]
                layerdir = self.layercontents[i][1]
                print "Processing Glyph Layer " + str(i) + ": " + layername,layerdir
                if layerdir in self.tree:
                    self.layers.append( Ulayer(layername, layerdir, ufodir = ufodir, layertree = self.tree[layerdir]['tree']) )
                else :
                    print "Glyph directory",layerdir, "missing"
                    sys.exit()

    def _readPlist(self, fn) :
        if fn in self.tree :
            return Uplist( fn = os.path.join(self.ufodir,fn) )
        else :
            print fn, "does not exist2"
            sys.exit()            

class Ulayer(dict) :
    def __init__(self,layername,layerdir,ufodir = None,layertree = None) :
        fulldir = os.path.join(ufodir,layerdir)
        self["contents"] = Uplist( fn = os.path.join(fulldir, "contents.plist") )
        for glyphn in sorted(self["contents"].keys()) :
            glifn = self["contents"][glyphn]
            if glifn in layertree :
                self[glyphn] = Uglif(fn = os.path.join(fulldir, glifn))
            else :
                print "Missing glif ",glifn
                sys.exit()



        
class Uplist(xmlitem) :
    
    def __init__(self, fn = None, parse = True ) :
        xmlitem.__init__(self, fn, parse)
        if fn : self.populate_dict()
    
    def populate_dict(self) :
        pl = self.etree[0]
        if pl.tag == "dict" :
            for i in range(0,len(pl),2):
                key = pl[i].text
                self[key] = pl[i+1].text
        else : # Assume array of 2 element arrays (eg layercontents.plist)
            for i in range(len(pl)) :
                self[i] = [ pl[i][0].text, pl[i][1].text ]
                
     
                
class Uglif(xmlitem) :
    
    def __init__(self, fn = None, parse = True ) :
        xmlitem.__init__(self, fn, parse)
        if fn : self.populate_dict()
    
    def populate_dict(self) :
        et = self.etree
        for i in range(len(et)) :
            self[et[i].tag] = { 'index' : i, 'element' : et[i] }
        


# ###############################################################################################################################


if __name__ == '__main__' :

    font = Ufont(ufodir=sys.argv[1])
    
    testn = "CySmO"
    if testn in font.layers[0] :
        glif = font.layers[0][testn]
        for i in glif :
            print "-------------------"
            print i
            print glif[i]
            index = glif[i]['index']
            print glif.etree[index]
        
    sys.exit()
    
    uinput = sys.argv[1]
    if not os.path.isdir(uinput) :
        print uinput + " not a directory"
        sys.exit()
    
    # Read list of files and folders in top 2 levels; anything at lower levels just needs copying
    (upath,ubase) = os.path.split(uinput)
    utree={}
    for name in os.listdir(uinput) :
        item={}
        if os.path.isdir(os.path.join(uinput, name)) :
            item["type"] = "d"
            item["contents"] = {}
            for subname in os.listdir(os.path.join(uinput, name)) :
                item["contents"][subname] = {}
                if os.path.isdir(os.path.join(uinput, name, subname)) :
                    item["contents"][subname]["type"] = "d"
                else:
                    item["contents"][subname]["type"] = "f"
        else :
            item["type"] = "f"
        utree[name] = item
    
    for i in utree :
        print i, utree[i]
        #for j in utree[i] :
         #   print j, utree[i][j]
            


    sys.exit()
        
        
    
    
    # Sort the key,value pairs alphabetically
    if item.etree.tag == 'plist' :
        item.etree.doctype = 'plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'
        pldict = item.etree[0]
        plist={}
        for i in range(0,len(pldict),2):
            key = pldict[i].text
            plist[key] = [pldict[i],pldict[i+1]]
        
        i=0    
        for key in sorted(plist.keys()):
            item.etree[0][i]=plist[key][0]
            item.etree[0][i+1]=plist[key][1]
            i=i+2

    newitem = deepcopy(item)
    newitem.xmlstring=""
    output = ETWriter(newitem.etree)
    if newitem.etree.tag == 'plist' : output.indentFirst = ""
    output.serialize_xml(newitem.write_to_xml)
    
    outfile=open("xmltest.xml","w")
    outfile.write(newitem.xmlstring)
    outfile.close
    
    
