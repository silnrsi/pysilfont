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
from UFOtestlib1 import *

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
            if self.UFOversion == "2" : # Create a dummy layer contents so 2 & 3 can be handled the same
                self.layercontents = Uplist()
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