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
            #self.path,base) = os.path.split(ufodir)
            self.metainfo = self._readPlist("metainfo.plist")
            self.UFOversion = self.metainfo["formatVersion"].text
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
                #print self.layercontents[i][0][1].text
                layername = self.layercontents[i][0].text
                layerdir = self.layercontents[i][1].text
                print "Processing Glyph Layer " + str(i) + ": " + layername,layerdir
                if layerdir in self.tree:
                    self.layers.append( Ulayer(layername, layerdir, ufodir = ufodir, layertree = self.tree[layerdir]['tree']) )
                else :
                    print "Glyph directory",layerdir, "missing"
                    sys.exit()
            # Set initial defaults for outparams            
            self.outparams = { "indentIncr" : "  ", "indentFirst" : "  ", "plistIndentFirst" : "" }
            self.outparams["UFOversion"] = self.UFOversion

    def _readPlist(self, filen) :
        print filen
        if filen in self.tree :
            return Uplist( self.ufodir,filen )
        else :
            print dirn,filen, "does not exist2"
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
        if self.UFOversion <> UFOversion : self.metainfo["formatVersion"].text = str(UFOversion)
        self.metainfo["creator"].text = "org.sil.sripts" # What should this be? pysilfont?
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
        

class Ulayer(dict) :
    
    def __init__(self,layername,layerdir,ufodir = None,layertree = None) :
        self.layername = layername
        self.layerdir = layerdir
        fulldir = os.path.join(ufodir,layerdir)
        self.contents = Uplist( fulldir, "contents.plist" )
        for glyphn in sorted(self.contents.keys()) :
            glifn = self.contents[glyphn].text
            if glifn in layertree :
                self[glyphn] = Uglif(fulldir, glifn)
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
            glyph = self[glyphn]
            writeXMLobject(glyph, params, fulldir, glyph.filen)
            
class Uplist(xmlitem) :
    
    def __init__(self, dirn = None, filen = None, parse = True) :
        xmlitem.__init__(self, dirn, filen, parse)
        self.type = "plist"
        if filen : self.populate_dict()
    
    def populate_dict(self) :
        pl = self.etree[0]
        if pl.tag == "dict" :
            for i in range(0,len(pl),2):
                key = pl[i].text
                self[key] = pl[i+1]
        else : # Assume array of 2 element arrays (eg layercontents.plist)
            for i in range(len(pl)) :
                self[i] = pl[i]
    
    

class Uglif(xmlitem) :
    
    def __init__(self, dirn = None, filen = None, parse = True) :
        xmlitem.__init__(self, dirn, filen, parse)
        self.type="glif"
        if filen : self.populate_dict()
    
    def populate_dict(self) :
        et = self.etree
        for i in range(len(et)) :
            self[et[i].tag] = { 'index' : i, 'element' : et[i] }
            
def writeXMLobject(object,params, dirn, filen) :
    if object.type == "plist" :
        indentFirst = params["plistIndentFirst"]
        object.etree.doctype = 'plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'
    else :
        indentFirst = params["indentFirst"]
        
    etw = ETWriter(object.etree, indentIncr = params["indentIncr"], indentFirst = indentFirst)
    etw.serialize_xml(object.write_to_xml)
    object.write_to_file(dirn,filen)