#!/usr/bin/env python
'Classes and functions for use handling Ufont UFO font objects in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET
import sys, os, copy, shutil
import collections
from genlib import *

_glifElements  = ('advance', 'unicode', 'note',   'image',  'guideline', 'anchor', 'outline', 'lib')
_glifElemMulti = (False,     True,      False,    False,    True,       True,     False,     False)
_glifElemF1    = (True,      True,      False,    False,    False,       False,    True,      True)

_illegalChars = "\"*+/:<>?[\]|" + chr(0x7F)
for i in range(0,32) : _illegalChars += chr(i)
_illegalChars = list(_illegalChars)
_reservedNames = "CON PRN AUX CLOCK$ NUL COM1 COM2 COM3 COM4 PT1 LPT2 LPT3".lower().split(" ")

class _Ucontainer(object) :
    # Parent class for other objects (eg Ulayer)
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

class Uelement(_Ucontainer) :
    # Class for an etree element. Mainly used as a parent class
    # For each tag in the element, returns list of sub-elements with that tag
    def __init__(self,element) :
        self.element = element
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

class Utextfile(object) :
    # Generic object for handling non-xml text files
    def __init__(self, font = None, dirn = None, filen = None) :
        if dirn is None and font: dirn = font.ufodir
        self.type = "textfile"
        self.font = font
        if filen and dirn : self.populate_dict()
    

class Ufont(object) :
    """ Object to hold all the data from a UFO"""
    
    def __init__(self, ufodir = None, logger = None ) :
        if not logger : logger = loggerobj() # Will only log message to screen
        self.logger = logger
        if ufodir:
            self.ufodir = ufodir
            self.logger.log( 'Reading UFO: ' + ufodir, 'P')
            if not os.path.isdir(ufodir) :
                self.logger.log(ufodir + " is not a directory","S")
            # Read list of files and folders in top 4 levels; anything at lower levels just needs copying
            self.dtree=dirTree(ufodir)
            self.metainfo = self._readPlist("metainfo.plist")
            self.UFOversion = self.metainfo["formatVersion"][1].text
            # Read other top-level plists
            if "fontinfo.plist" in self.dtree : self.fontinfo = self._readPlist("fontinfo.plist")
            if "groups.plist" in self.dtree : self.groups = self._readPlist("groups.plist")
            if "kerning.plist" in self.dtree : self.kerning = self._readPlist("kerning.plist")
            if "lib.plist" in self.dtree : self.lib = self._readPlist("lib.plist")
            if self.UFOversion == "2" : # Create a dummy layer contents so 2 & 3 can be handled the same
                self.layercontents = Uplist(font = self)
                self.dtree['layercontents.plist'] = dirTreeItem(read = True, added = True, fileObject = self.layercontents, fileType = "xml")
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
                self.logger.log( "Processing Glyph Layer " + str(i) + ": " + layername + layerdir, "I")
                layer = Ulayer(layername, layerdir, self)
                if layer :
                    self.layers.append( layer )
                else :
                    self.logger.log( "Glyph directory " + layerdir + " missing", "S")
            # Set initial defaults for outparams            
            self.outparams = { "indentIncr" : "  ", "indentFirst" : "  ", "indentML" : False, "plistIndentFirst" : "", 'sortDicts' : True , 'precision' : 6}
            self.outparams["renameGlifs"] = True
            self.outparams["UFOversion"] = self.UFOversion
            self.outparams["attribOrders"] = {
                'glif' : makeAttribOrder([
                    'pos', 'width', 'height', 'fileName', 'base', 'xScale', 'xyScale', 'yxScale', 
                    'yScale', 'xOffset', 'yOffset', 'x', 'y', 'angle', 'type', 'smooth', 'name', 
                    'format', 'color', 'identifier'])
                }

    def _readPlist(self, filen) :
        if filen in self.dtree :
            plist = Uplist(font = self, filen = filen)
            self.dtree[filen].setinfo(read = True, fileObject = plist, fileType = "xml")
            return plist
        else :
            self.logger.log( ufodir + " " + filen + " does not exist2", "S")
    
    def write(self, outdir) :
        # Write UFO out to disk, based on values set in self.outparams
        self.logger.log( "Processing font for output", "P")
        if not os.path.exists(outdir) :
            try:
                os.mkdir(outdir)
            except Exception as e :
                print e
                sys.exit(1)
        if not os.path.isdir(outdir) :
            self.logger.log( outdir + " not a directory", "S")
            
        # If output UFO already exists, need to open so only changed files are updated and redundant files deleted
        if outdir == self.ufodir : # In special case of output and input being the same, simply copy the input font
            ofontOrig = copy.deepcopy(self)
        else :
            if not os.path.exists(outdir) : # If outdir does not exist, create it
                try:
                    os.mkdir(outdir)
                except Exception as e :
                    print e
                    sys.exit(1)
                ofontOrig = None
            else:
                if not os.path.isdir(outdir) : self.logger.log( outdir + " not a directory", "S")
                dirlist = os.listdir(outdir)
                if dirlist == [] : # Outdir is empty
                    ofontOrig = None
                elif "metainfo.plist" in dirlist :
                    self.logger.log("Output UFO already exists - reading for comparison", "P")
                    ofontOrig = Ufont(outdir, logger = self.logger)
                else:
                    self.logger.log( outdir + " exists but is not a UFO", "S")
        # Update version info etc
        UFOversion = self.outparams["UFOversion"]
        self.metainfo["formatVersion"][1].text = str(UFOversion)
        self.metainfo["creator"][1].text = "org.sil.scripts"

        # Set standard UFO files for output
        dtree = self.dtree
        setFileForOutput(dtree, "metainfo.plist", self.metainfo, "xml")
        if "fontinfo" in self.__dict__ : setFileForOutput(dtree, "fontinfo.plist", self.fontinfo,  "xml")
        if "groups" in self.__dict__ : setFileForOutput(dtree, "groups.plist", self.groups, "xml")
        if "kerning" in self.__dict__ : setFileForOutput(dtree, "kerning.plist", self.kerning, "xml")
        if "lib" in self.__dict__ : setFileForOutput(dtree, "lib.plist", self.lib, "xml")
        if UFOversion == "3" : setFileForOutput(dtree, "layercontents.plist", self.layercontents, "xml")
        # Set glyph layers for output
        for layer in self.layers : layer.setForOutput()
        
        # Write files to disk
        
        odtree = ofontOrig.dtree if ofontOrig else {}
        self.logger.log("Writing font to " + outdir, "P")
        
        writeToDisk(dtree, outdir, self, odtree,)

class Ulayer(_Ucontainer) :
    
    def __init__(self, layername, layerdir, font) :
        self._contents = {}
        layerdtree = font.dtree.subTree(layerdir)
        if not layerdtree : return
        font.dtree[layerdir].read = True
        self.layername = layername
        self.layerdir = layerdir
        self.font = font
        fulldir = os.path.join(font.ufodir,layerdir)
        self.contents = Uplist( font = font, dirn = fulldir, filen = "contents.plist" )
        layerdtree["contents.plist"].setinfo(read = True, fileObject = self.contents, fileType = "xml")
        
        if font.UFOversion == "3" :
            if 'layerinfo.plist' in layerdtree : 
                self.layerinfo = Uplist( font = font, dirn = fulldir, filen = "layerinfo.plist" )
                layerdtree["layerinfo.plist"].setinfo(read = True, fileObject = self.layerinfo, fileType = "xml")
                
        for glyphn in sorted(self.contents.keys()) :
            glifn = self.contents[glyphn][1].text
            if glifn in layerdtree :
                self._contents[glyphn] = Uglif(layer = self, filen = glifn)
                layerdtree[glifn].setinfo( read = True, fileObject = self._contents[glyphn], fileType = "xml")
                if glyphn <> self._contents[glyphn].name : self.font.logger.log( "Glyph name mismatch for " + glyphn, "W")
            else :
                self.font.logger.log( "Missing glif " + glifn + " in " + fulldir, "S")
                
    def setForOutput(self) :
        
        UFOversion = self.font.outparams["UFOversion"]
        dtree = self.font.dtree.subTree(self.layerdir)
        if self.font.outparams["renameGlifs"] : self.renameGlifs()

        setFileForOutput(dtree,"contents.plist", self.contents, "xml")
        if "layerinfo" in self.__dict__ and UFOversion == "3" : setFileForOutput(dtree, "layerinfo.plist", self.layerinfo, "xml")
        
        for glyphn in self :
            glyph = self._contents[glyphn]
            if UFOversion == "2" : glyph.convertToFormat1()
            if glyph.rebuildETflag : glyph.rebuildET()
            setFileForOutput(dtree,glyph.filen, glyph, "xml")
            
    def renameGlifs(self) :
        namelist=[]
        for glyphn in sorted(self.keys()) :
            glyph = self._contents[glyphn]
            filename = makeFileName(glyphn,namelist)
            namelist.append(filename.lower())
            filename += ".glif"
            if filename <> glyph.filen :
                self.renameGlif(glyphn,glyph,filename)
            
    
    def renameGlif(self,glyphn,glyph,newname) :
        self.font.logger.log( "Renaming glif for " + glyphn + " from " + glyph.filen + " to " + newname, "I")
        glyph.filen = newname
        self.contents[glyphn][1].text = newname
        
class Uplist(xmlitem) :
    
    def __init__(self, font = None, dirn = None, filen = None, parse = True) :
        if dirn is None and font: dirn = font.ufodir
        xmlitem.__init__(self, dirn, filen, parse)
        self.type = "plist"
        self.font = font
        self.outparams = None
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
    
class Uglif(xmlitem) :
    # Unlike plists, glifs can have multiples of some sub-elements (eg anchors) so create lists for those
    
    def __init__(self, layer = None, filen = None, parse = True) :
        if layer is None :
            dirn = None
        else :
            dirn = os.path.join(layer.font.ufodir, layer.layerdir)
        xmlitem.__init__(self, dirn, filen, parse)
        self.type="glif"
        self.layer = layer
        self.outparams = None
        self.rebuildETflag = False # Flag to see if self.etree needs rebuilding, eg if sub-objects are changed
        
        # Set initial values for sub-objects
        for i in range(len(_glifElements)) :
            elementn = _glifElements[i]
            if _glifElemMulti[i] :
                self._contents[elementn] = []
            else :
                self._contents[elementn] = None

        if self.etree is not None : self.process_etree()
        if self.rebuildETflag : self.rebuildET()

    def process_etree(self) :
        et = self.etree
        self.name = getattrib(et,"name")
        self.format = getattrib(et,"format")
        if self.format is None :
            if self.layer.font.UFOversion == "3" :
                self.format = '2'
            else :
                self.format = '1'
        previouselem = 0 # Flag to help check if sub-objects in normalised order
        for i in range(len(et)) :
            element = et[i]
            tag = element.tag
            index  = _glifElements.index(tag)
            multi  = _glifElemMulti[index]
            F1elem = _glifElemF1[index]
            if F1elem or self.format == '2' :
                if multi : 
                    self._contents[tag].append(self.makeObject(tag,element))
                else:
                    self._contents[tag] = self.makeObject(tag,element)
            if i < previouselem : self.rebuildETflag = True
            previouselem = i

        # Convert UFO2 style anchors to UFO3 anchors
        if self._contents['outline'] is not None and self.format == "1":
            for contour in self._contents['outline'].contours[:] :
                if contour.UFO2anchor :
                    del contour.UFO2anchor["type"] # remove type="move"
                    self.add('anchor',contour.UFO2anchor)
                    self._contents['outline'].removeobject(contour, "contour")
                    self.rebuildETflag = True
                  
        self.format = "2"
        et.set("format","2")

    def rebuildET(self) :
        # All sub-elements are duplicated in the sub-objects so the library does not keep the
        # originals in the glif's etree updated.  The etree also may need rebuilding to normalise
        # the sub-objects order
        et = self.etree
        
        # Remove existing sub-elements
        
        while et.getchildren() : et.remove(et.getchildren()[0])

        # Insert new elements
        for i in range(len(_glifElements)) :
            F1 = _glifElemF1[i]
            if F1 or self.format == "2" : # Check element is valid for glif format
                elementn = _glifElements[i]
                item = self._contents[elementn]
                if item is not None :
                    if _glifElemMulti[i] :
                        for object in item :
                            et.append(object.element)
                    else :
                        et.append(item.element)
        self.rebuildETflag = False
    
    def add(self,ename,attrib) :
        # Add an element and corrensponding object to a glif
        element = ET.Element(ename,attrib)
        index = _glifElements.index(ename)
        multi = _glifElemMulti[index]
        
        # Check element does not already exist for single elements
        if self._contents[ename] and not multi :
            message = "Already an " + enam + "in glif"
            if self.layer : self.layer.font.logger.log( message, "S")
        
        # Add new object
        if multi :
            self._contents[ename].append(self.makeObject(ename,element))
        else:
            self._contents[ename] = self.makeObject(ename,element)
        
        self.rebuildETflag = True
            
    def remove(self, ename, index = None, object = None ) :
        # Remove object from a glif
        # For multi objects, an index or object must be supplied to identify which
        # to delete
        eindex = _glifElements.index(ename)
        multi = _glifElemMulti[eindex]
        item = self._contents[ename]

        # Delete the object
        if multi :
            if index:
                object = item[index]
            else :
                index = item.index(object)
            del item[index]
        else :
            object = item
            del self._contents[ename]

        self.rebuildETflag = True
    
    def convertToFormat1(self) :
        # Convert to a glif format of 1 (for UFO2) prior to writing out
        et = self.etree
        self.format = "1"
        et.set("format","1")
        # Change anchors to UFO2 style anchors
        for anchor in self._contents['anchor'][:] :
            element = anchor.element
            for attrn in ('colour', 'indentifier') : # Remove format 2 attributes
                if attrn in element.attrib : del element.attrib[attrn]
            element.attrib['type'] = 'move'
            contelement = ET.Element("contour")
            contelement.append(ET.Element("point",element.attrib))            
            self._contents['outline'].appendobject(Ucontour(self._contents['outline'],contelement),"contour")
            self.remove('anchor',object=anchor)

        self.rebuildETflag = True
            
    def makeObject(self, type, element) :
        if type == 'advance'   : return Uadvance(self,element)
        if type == 'unicode'   : return Uunicode(self,element)
        if type == 'outline'   : return Uoutline(self,element)
        if type == 'lib'       : return Ulib(self,element)
        if type == 'note'      : return Unote(self,element)
        if type == 'image'     : return Uimage(self,element)
        if type == 'guideline' : return Uguideline(self,element)
        if type == 'anchor'    : return Uanchor(self,element)
         
class Uadvance(Uelement) :
    
    def __init__(self, glif, element) :
        super(Uadvance,self).__init__(element)

class Uunicode(Uelement) :
    
    def __init__(self, glif, element) :
        super(Uunicode,self).__init__(element)
 
class Unote(Uelement) :
    
    def __init__(self, glif, element) :
        super(Unote,self).__init__(element)
 
class Uimage(Uelement) :
    
    def __init__(self, glif, element) :
        super(Uimage,self).__init__(element)
 
class Uguideline(Uelement) :
    
    def __init__(self, glif, element) :
        super(Uguideline,self).__init__(element)

class Uanchor(Uelement) :
    
    def __init__(self, glif, element) :
        super(Uanchor,self).__init__(element)
  
class Uoutline(Uelement) :
    
    def __init__(self, glif, element) :
        super(Uoutline,self).__init__(element)
        self.glif = glif
        self.components = []
        self.contours = []
        for tag in self._contents :
            if tag == "component" :
                for component in self._contents[tag] :
                    self.components.append( Ucomponent(self,component) )
            if tag == "contour" :
                for contour in self._contents[tag] :
                    self.contours.append( Ucontour(self,contour) )

    def removeobject(self,object,type) :
        super(Uoutline,self).remove(object.element)
        if type == "component" : self.components.remove(object)
        if type == "contour" : self.contours.remove(object)
        
    def appendobject(self,object,type) :
        super(Uoutline,self).append(object.element)
        if type == "component" : self.components.append(object)
        if type == "contour" : self.contours.append(object)
    
    def insertobject(self,index,object,type) :
        super(Uoutline,self).insert(index,object.element)
        if type == "component" : self.components.insert(index,object)
        if type == "contour" : self.contours.insert(index,object)
    
class Ucomponent(Uelement) :
    
    def __init__(self, outline, element) :
        super(Ucomponent,self).__init__(element)
 
class Ucontour(Uelement) :
    
    def __init__(self, outline, element) :
        super(Ucontour,self).__init__(element)
        self.UFO2anchor = None
        points = self._contents['point']
        # Identify UFO2-style anchor points
        if len(points) == 1 and "type" in points[0].attrib :
            if points[0].attrib["type"] == "move" :
                self.UFO2anchor = points[0].attrib
        
class Ulib(Uelement) :
    # For glif lib elements; top-level lib files use Uplist
    def __init__(self, glif, element) :
        super(Ulib,self).__init__(element)

def writeXMLobject(dtreeitem, font, dirn, filen, odtreeitem) :
    params = font.outparams
    object = dtreeitem.fileObject
    if object.outparams : params = object.outparams # override default params with object-specific ones
    indentFirst = params["indentFirst"]
    attribOrder = {}
    if object.type in params['attribOrders'] : attribOrder = params['attribOrders'][object.type]
    if object.type == "plist" :
        indentFirst = params["plistIndentFirst"]
        object.etree.doctype = 'plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'
        
    # Format ET data if any data parameters are set
    if params["sortDicts"] or params["precision"] is not None : normETdata(object.etree, params)

    etw = ETWriter(object.etree, attributeOrder = attribOrder, indentIncr = params["indentIncr"], indentFirst = indentFirst, indentML = params["indentML"])
    etw.serialize_xml(object.write_to_xml)
    # Now we have the output xml, need to compare with existing item's xml, if present
    changed = True
    if odtreeitem:
        if odtreeitem.fileObject.inxmlstr == object.outxmlstr : changed = False
    if changed : object.write_to_file(dirn,filen)
    dtreeitem.written = True # Mark as True, even if not changed - the file should still be there!
    
def setFileForOutput(dtree, filen, fileObject, fileType) : # Put details in dtree, creating item if needed
    if not filen in dtree :
        dtree[filen] = dirTreeItem()
        dtree[filen].added = True
    dtree[filen].setinfo(fileObject = fileObject, fileType = fileType, towrite = True)
    
def writeToDisk(dtree, outdir, font, odtree = {}, logindent = "") :

    # Make lists of items in dtree and odtree with type prepended for sorting and comparison purposes
    dtreelist = []
    for filen in dtree : dtreelist.append(dtree[filen].type+filen)
    dtreelist.sort()
    odtreelist = []
    for filen in odtree : odtreelist.append(odtree[filen].type+filen)
    odtreelist.sort()
    okey = odtreelist.pop(0) if odtreelist <> [] else None
    
    for key in dtreelist :
        type = key[0:1]
        filen = key[1:]
        dtreeitem = dtree[filen]

        while okey and okey < key : # Item in output UFO no longer needed
            ofilen = okey[1:]
            if okey[0:1] == "f" :
                font.logger.log('Deleting a '+ ofilen + ' from existing output UFO', "W")
                os.remove(os.path.join(outdir,ofilen))
            else:
                font.logger.log('Deleting directory '+ ofilen + ' from existing output UFO', "W")
                shutil.rmtree(os.path.join(outdir,ofilen))
            okey = odtreelist.pop(0) if odtreelist <> [] else None
        
        if key == okey :
            odtreeitem = odtree[filen]
            okey = odtreelist.pop(0) if odtreelist <> [] else None # Ready for next loop
        else :
            odtreeitem = None
        
        if dtreeitem.type == "f" :
            if dtreeitem.towrite :
                font.logger.log(logindent + filen, "V")
                if dtreeitem.fileType == "xml" :
                    writeXMLobject(dtreeitem,font,outdir,filen,odtreeitem)
                else :
                    pass #@@@ add code for other file types
            else :
                if not dtreeitem.added : font.logger.log('Skipping invalid file '+ filen + ' from input UFO', "W")
                if odtreeitem:
                    if not odtreeitem.added : 
                        font.logger.log('Deleting '+ filen + ' from existing output UFO', "W")
                        os.remove(os.path.join(outdir,filen))
                    
        else : # Must be directory
            if not dtreeitem.read :
                font.logger.log(logindent + "Skipping invalid input directory " + filen)
                if odtreeitem :
                    font.logger.log('Deleting directory '+ filen + ' from existing output UFO', "W")
                    shutil.rmtree(os.path.join(outdir,filen))
                continue
            font.logger.log(logindent + "Processing " + filen + " directory", "I")
            subdir = os.path.join(outdir,filen)
            if not os.path.exists(subdir) : # If outdir does not exist, create it
                try:
                    os.mkdir(subdir)
                except Exception as e :
                    print e
                    sys.exit(1)
            subodtree = odtreeitem.dirtree if odtreeitem else {}
            subindent = logindent + "  "
            writeToDisk(dtreeitem.dirtree, subdir, font, subodtree, subindent)
            if os.listdir(subdir) == [] : os.rmdir(subdir) # Delete directory if empty
            
    

def normETdata(element,params) :
    # Recursively normalise the data an an ElementTree element
    for subelem in list(element) :
        normETdata(subelem,params)
    # Process based on tag
    tag = element.tag
    val = element.text
    precision = params["precision"]
    if tag in ("integer","real") and precision is not None:
        num = round(float(val),precision)
        if num ==int(num) :
            element.tag = "integer"
            element.text = "{:.0f}".format(num)
        else :
            element.tag = "real"
            element.text = "{}".format(num)
    if params["sortDicts"] and tag == "dict" :
        edict={}
        elist=[]
        for i in range(0,len(element),2):
            edict[element[i].text] = [element[i],element[i+1]]
            elist.append(element[i].text)
        keylist = sorted(edict.keys())
        if elist <> keylist :
            i=0
            for key in keylist :
                element[i] = edict[key][0]
                element[i+1] = edict[key][1]
                i=i+2
            
def getattrib(element,attrib) :
    if attrib in element.attrib :
        return element.attrib[attrib]
    else: return None

def makeFileName(name,namelist=[]) :
    # Replace illegal characters and add _ after UC letters
    newname=""
    for x in name :
        if x in _illegalChars :
            x = "_"
        else :
            if x <> x.lower() : x += "_"
        newname += x
    # Replace initial . if present
    if newname[0] == "." : newname = "_" + newname[1:]
    parts=[]
    for part in newname.split(".") :
        if part in _reservedNames :
            part = "_" + part
        parts.append(part)
    name = ".".join(parts)
    if name.lower() in namelist : # case-insensitive name already used, so add a suffix
        newname = None
        i=1
        while newname is None :
            test = name + '{0:015d}'.format(i)
            if not (test.lower() in namelist) : newname = test
            i += 1
        name = newname
    return name
