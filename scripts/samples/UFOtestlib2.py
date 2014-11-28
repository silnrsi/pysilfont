#!/usr/bin/env python
'UFO handling script under development'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET
import sys, os
from UFOtestlib1 import *

class Ucontainer(object) :
    # Parent class for other objects (eg Ulayer)
    def __init_(self) :
        self._contents = {}
    # Define methods so it acts like an imutable container
    # (changes should be made via changing self.etree elements or object functions)
    def __len__(self):
        return len(self._contents)
    def __getitem__(self, key):
        return self._contents[key]
    def __iter__(self):
        return iter(self._contents)
    def keys(self) :
        return self._contents.keys()
    
class Ufont(object) :
    """ Object to hold all the data from a UFO"""
    
    def __init__(self, ufodir = None ) :
        if ufodir:
            self.ufodir = ufodir
            print 'Opening UFO for input: ',ufodir
            if not os.path.isdir(ufodir) :
                print ufodir + " not a directory"
                sys.exit()
            # Read list of files and folders in top 2 levels; anything at lower levels just needs copying
            self.tree=dirTree(ufodir)
            #self.path,base) = os.path.split(ufodir)
            self.metainfo = self._readPlist("metainfo.plist")
            self.UFOversion = self.metainfo["formatVersion"][1].text
            # Read other top-level plists
            if "fontinfo.plist" in self.tree : self.fontinfo = self._readPlist("fontinfo.plist")
            if "groups.plist" in self.tree : self.groups = self._readPlist("groups.plist")
            if "kerning.plist" in self.tree : self.kerning = self._readPlist("kerning.plist")
            if "lib.plist" in self.tree : self.lib = self._readPlist("lib.plist")
            if self.UFOversion == "2" : # Create a dummy layer contents so 2 & 3 can be handled the same
                self.layercontents = Uplist(font = self)
                dummylc = "<plist>\n<array>\n<array>\n<string>public.default</string>\n<string>glyphs</string>\n</array>\n</array>\n</plist>"
                self.layercontents.etree = ET.fromstring(dummylc)
                self.layercontents.populate_dict()
            else :
                self.layercontents = self._readPlist("layercontents.plist")
            # Process the glyphs directories)
            self.layers = []
            for i in sorted(self.layercontents.keys() ) :
                layername = self.layercontents[i][0].text
                layerdir = self.layercontents[i][1].text
                print "Processing Glyph Layer " + str(i) + ": " + layername,layerdir
                if layerdir in self.tree:
                    self.layers.append( Ulayer(layername, layerdir, self) )
                else :
                    print "Glyph directory",layerdir, "missing"
                    sys.exit()
            # Set initial defaults for outparams            
            self.outparams = { "indentIncr" : "  ", "indentFirst" : "  ", "plistIndentFirst" : "", 'sortPlists' : True }
            self.outparams["UFOversion"] = self.UFOversion
            self.outparams["attribOrders"] = {
                'glif' : makeAttribOrder([
                    'pos', 'width', 'height', 'fileName', 'base', 'xScale', 'xyScale', 'yxScale', 
                    'yScale', 'xOffset', 'yOffset', 'x', 'y', 'angle', 'type', 'smooth', 'name', 
                    'format', 'color', 'identifier'])
                }

    def _readPlist(self, filen) :
        if filen in self.tree :
            return Uplist(font = self, filen = filen)
        else :
            print ufodir,filen, "does not exist2"
            sys.exit()
    
    def write(self, outdir) :
        ''' Write UFO out to disk, based on values set in self.outparams'''
        
        if not os.path.exists(outdir) :
            try:
                os.mkdir(outdir)
            except Exception as e :
                print e
                sys.exit()
        if not os.path.isdir(outdir) :
            print outdir + " not a directory"
            sys.exit()
        UFOversion = self.outparams["UFOversion"]
        # Update metainfo.plist and write out
        self.metainfo["formatVersion"][1].text = str(UFOversion)
        self.metainfo["creator"][1].text = "org.sil.sripts" # What should this be? pysilfont?
        writeXMLobject(self.metainfo, self.outparams, outdir, "metainfo.plist")
        # Write out other plists
        if "fontinfo" in self.__dict__ : writeXMLobject(self.fontinfo, self.outparams, outdir, "fontinfo.plist")
        if "groups" in self.__dict__ : writeXMLobject(self.groups, self.outparams, outdir, "groups.plist")
        if "kerning" in self.__dict__ : writeXMLobject(self.kerning, self.outparams, outdir, "kerning.plist")
        if "lib" in self.__dict__ : writeXMLobject(self.lib, self.outparams, outdir, "lib.plist")
        if UFOversion == 3 : writeXMLobject(self.layercontents, self.outparams, outdir, "layercontents.plist")
        # Write out glyph layers
        for layer in self.layers : layer.write(outdir,self.outparams)
        # Copy other files and directories


class Ulayer(Ucontainer) :
    
    def __init__(self, layername, layerdir, font) :
        self._contents = {}
        self.layername = layername
        self.layerdir = layerdir
        self.font = font
        layertree = font.tree[layerdir]['tree']
        fulldir = os.path.join(font.ufodir,layerdir)
        self.contents = Uplist( font = font, dirn = fulldir, filen = "contents.plist" )
        for glyphn in sorted(self.contents.keys()) :
            glifn = self.contents[glyphn][1].text
            if glifn in layertree :
                self._contents[glyphn] = Uglif(layer = self, filen = glifn)
            else :
                print "Missing glif ",glifn, "in", fulldir
                sys.exit()
                
    def write(self,outdir,params) :
        print "Processing layer", self.layername
        fulldir = os.path.join(outdir,self.layerdir)
        if not os.path.exists(fulldir) :
            try:
                os.mkdir(fulldir)
            except Exception as e :
                print e
                sys.exit()
        if not os.path.isdir(fulldir) :
            print fulldir + " not a directory"
            sys.exit()
        writeXMLobject(self.contents, params, fulldir, "contents.plist")
        for glyphn in self :
            glyph = self._contents[glyphn]
            writeXMLobject(glyph, params, fulldir, glyph.filen)
            
class Uplist(xmlitem) :
    
    def __init__(self, font = None, dirn = None, filen = None, parse = True) :
        if dirn is None :
            if font : dirn = font.ufodir
        xmlitem.__init__(self, dirn, filen, parse)
        self.type = "plist"
        self.font = font
        if filen and dirn : self.populate_dict()
    
    def populate_dict(self) :
        self._contents.clear() # Clear existing contents, if any
        pl = self.etree[0]
        if pl.tag == "dict" :
            for i in range(0,len(pl),2):
                key = pl[i].text
                self._contents[key] = [pl[i],pl[i+1]] # The two elements for the item
        else : # Assume array of 2 element arrays (eg layercontents.plist)
            for i in range(len(pl)) :
                self._contents[i] = pl[i]
    
    def sort(self) : # For dict-based plists sort keys alphabetically
        if self.etree[0].tag == "dict" :
            self.populate_dict() # Recreate dict in case changes have been made
            i=0
            for key in sorted(self.keys()):
                self.etree[0][i]=self._contents[key][0]
                self.etree[0][i+1]=self._contents[key][1]
                i=i+2
    
class Uglif(xmlitem) :
    
    def __init__(self, layer = None, filen = None, parse = True) :
        if layer is None :
            dirn = None
        else :
            dirn = os.path.join(layer.font.ufodir, layer.layerdir)
        xmlitem.__init__(self, dirn, filen, parse)
        self.type="glif"
        self.layer = layer
        if filen and dirn : self.populate_dict()
    
    def populate_dict(self) :
        self._contents.clear() # Clear existing contents, if any
        et = self.etree
        for i in range(len(et)) :
            tag = et[i].tag
            self._contents[tag] = { 'index' : i, 'element' : et[i] }
            if tag == 'outline' : self.outline = Uoutline(self)

class Uoutline(Ucontainer) :
    
    def __init__(self, glif, element = None) :
        self.contents = {}
        if element is None : element = glif['outline']['element']
        print ">>>>>>>>>>>>>>>",element
        

def writeXMLobject(object, params, dirn, filen) :
    if object.outparams : params = object.outparams # override default params with object-specific ones
    indentFirst = params["indentFirst"]
    attribOrder = {}
    if object.type in params['attribOrders'] : attribOrder = params['attribOrders'][object.type]
    if object.type == "plist" :
        indentFirst = params["plistIndentFirst"]
        object.etree.doctype = 'plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'
        if params["sortPlists"] : object.sort()

    etw = ETWriter(object.etree, attributeOrder = attribOrder, indentIncr = params["indentIncr"], indentFirst = indentFirst)
    etw.serialize_xml(object.write_to_xml)
    object.write_to_file(dirn,filen)