#!/usr/bin/env python
'Classes and functions for use handling Ufont UFO font objects in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from xml.etree import cElementTree as ET
import sys, os, copy, shutil, filecmp
import collections
import silfont.core
import silfont.util as UT
import silfont.etutil as ETU

_glifElemMulti = ('unicode', 'guideline', 'anchor') # glif elements that can occur multiple times
_glifElemF1 = ('advance','unicode','outline','lib') # glif elements valid in format 1 glifs (ie UFO2 glfis)

# Define illegal characters and reserved names for makeFileName
_illegalChars = "\"*+/:<>?[\]|" + chr(0x7F)
for i in range(0,32) : _illegalChars += chr(i)
_illegalChars = list(_illegalChars)
_reservedNames = "CON PRN AUX CLOCK$ NUL COM1 COM2 COM3 COM4 PT1 LPT2 LPT3".lower().split(" ")

class _Ucontainer(object) :
    # Parent class for other objects (eg Ulayer)
    def __init_(self) :
        self._contents = {}
    # Define methods so it acts like an immutable container
    # (changes should be made via object functions etc)
    def __len__(self):
        return len(self._contents)
    def __getitem__(self, key):
        return self._contents[key]
    def __iter__(self):
        return iter(self._contents)
    def keys(self) :
        return self._contents.keys()

class _plist(object) :
    # Used for common plist methods inherited by Uplist and Ulib classes

    def addval(self,key,valuetype,value) : # For simple single-value elements
        if key in self._contents : self.font.logger.log("Attempt to add duplicate key " + key + " to plist", "X")
        dict = self.etree[0]

        keyelem = ET.Element("key")
        keyelem.text = key
        dict.append(keyelem)

        valelem = ET.Element(valuetype)
        valelem.text = value
        dict.append(valelem)

        self._contents[key] = [keyelem,valelem]

    def setval(self,key,valuetype,value) :
        if key in self._contents :
            self._contents[key][1].text = value
        else :
            self.addval(key,valuetype,value)

    def remove(self,key) :
        item = self._contents[key]
        self.etree[0].remove(item[0])
        self.etree[0].remove(item[1])
        del self._contents[key]

    def addelem(self,key,element) : # For non-simple elements (eg arrays) the calling script needs to build the etree element
        if key in self._contents : self.font.logger.log("Attempt to add duplicate key " + key + " to plist", "X")
        dict = self.etree[0]

        keyelem = ET.Element("key")
        keyelem.text = key
        dict.append(keyelem)
        dict.append(element)

        self._contents[key] = [keyelem,element]

    def setelem(self,key,element) :
        if key in self._contents : self.remove(key)
        self.addelem(key,element)

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

class UtextFile(object) :
    # Generic object for handling non-xml text files
    def __init__(self, font, dirn, filen) :
        self.type = "textfile"
        self.font = font
        self.filen = filen
        self.dirn = dirn
        if dirn == font.ufodir :
            dtree = font.dtree
        else :
            dtree = font.dtree.subtree(dirn)
            if not dtree : font.logger.log("Missing directory " + dirn, "X")
        if filen not in dtree:
            dtree[filen] = UT.dirTreeItem(added = True)
        dtree[filen].setinfo(read = True)
        dtree[filen].fileObject = self
        dtree[filen].fileType = "text"

    def write(self, dtreeitem, dir, ofilen, exists) :
        # For now just copies source to destination if changed
        inpath = os.path.join(self.dirn,self.filen)
        changed = True
        if exists : changed = not (filecmp.cmp(inpath, os.path.join(dir,self.filen)))
        if changed :
            try :
                shutil.copy2(inpath, dir)
            except Exception as e :
                print e
                sys.exit(1)
        dtreeitem.written = True

class Ufont(object) :
    """ Object to hold all the data from a UFO"""
    def __init__(self, ufodir, logger = None , params = None) :
        if logger is not None and params is not none : params.logger.log("Only supply a logger if params not set (since that has one)", "X")
        if params is None :
            params = silfont.core.params()
            if logger is not None: params.logger = logger
        self.params = params
        self.logger = params.logger
        self.ufodir = ufodir
        self.logger.log( 'Reading UFO: ' + ufodir, 'P')
        if not os.path.isdir(ufodir) :
            self.logger.log(ufodir + " is not a directory","S")
        # Read list of files and folders
        self.dtree=UT.dirTree(ufodir)
        # Read metainfo (which must exist)
        self.metainfo = self._readPlist("metainfo.plist")
        self.UFOversion = self.metainfo["formatVersion"][1].text
        # Read lib.plist then process pysilfont parameters if present
        libparams = {}
        if "lib.plist" in self.dtree :
            self.lib = self._readPlist("lib.plist")
            if "org.sil.pysilfontparams" in self.lib :
                elem = self.lib["org.sil.pysilfontparams"][1]
                if elem.tag <> "array" : self.logger.log("Invalid parameter XML lib.plist - org.sil.pysilfontparams must be an array","S")
                for param in elem :
                    parn = param.tag
                    if not(parn in params.paramclass) or params.paramclass[parn] <> "outparams" : self.logger.log("lib.plist org.sil.pysilfontparams must only contain outparams values: " + parn + " invalid", "S")
                    libparams[parn] = param.text
        # Create font-specific parameter set (with updates from lib.plist)  Prepend names with ufodir to ensure uniqueness if multiple fonts open
        params.addset(ufodir+"lib","lib.plist in "+ufodir,inputdict = libparams)
        params.sets[ufodir+"lib"].updatewith("command line", log = False) # Command line parameters override lib.plist ones
        params.addset(ufodir, copyset = "main")
        params.sets[ufodir].updatewith(ufodir+"lib",sourcedesc = "lib.plist")
        self.paramset = params.sets[ufodir]
        # Validate specific parameters
        if self.paramset["UFOversion"] not in ("","2","3") : self.logger.log ("UFO version must be 2 or 3","S")
        if sorted(self.paramset["glifElemOrder"]) <> sorted(self.params.sets["default"]["glifElemOrder"]) : self.logger.log("Invalid values for glifElemOrder", "S")


        # Create outparams based on values in paramset, building attriborders from separate attriborders.<type> parameters.
        self.outparams = {"attribOrders": {}}
        for parn in params.classes["outparams"] :
            value = self.paramset[parn]
            if parn[0:12] == 'attribOrders' :
                elemname = parn.split(".")[1]
                self.outparams["attribOrders"][elemname] = ETU.makeAttribOrder(value)
            else:
                self.outparams[parn] = value
        if self.outparams["UFOversion"] is "" : self.outparams["UFOversion"] = self.UFOversion

        # Read other top-level plists
        if "fontinfo.plist" in self.dtree : self.fontinfo = self._readPlist("fontinfo.plist")
        if "groups.plist" in self.dtree : self.groups = self._readPlist("groups.plist")
        if "kerning.plist" in self.dtree : self.kerning = self._readPlist("kerning.plist")
        if self.UFOversion == "2" : # Create a dummy layer contents so 2 & 3 can be handled the same
            if "glyphs" not in self.dtree : self.logger.log('No glyphs directory in font', "S")
            self.layercontents = Uplist(font = self)
            self.dtree['layercontents.plist'] = UT.dirTreeItem(read = True, added = True, fileObject = self.layercontents, fileType = "xml")
            dummylc = "<plist>\n<array>\n<array>\n<string>public.default</string>\n<string>glyphs</string>\n</array>\n</array>\n</plist>"
            self.layercontents.etree = ET.fromstring(dummylc)
            self.layercontents.populate_dict()
        else :
            self.layercontents = self._readPlist("layercontents.plist")
        # Process features.fea
        if "features.fea" in self.dtree :
             self.features = UfeatureFile(self,ufodir,"features.fea")
        # Process the glyphs directories)
        self.layers = []
        self.deflayer = None
        for i in sorted(self.layercontents.keys() ) :
            layername = self.layercontents[i][0].text
            layerdir = self.layercontents[i][1].text
            self.logger.log( "Processing Glyph Layer " + str(i) + ": " + layername + layerdir, "I")
            layer = Ulayer(layername, layerdir, self)
            if layer :
                self.layers.append( layer )
                if layername == "public.default" : self.deflayer = layer
            else :
                self.logger.log( "Glyph directory " + layerdir + " missing", "S")
        if self.deflayer is None : self.logger.log("No public.default layer", "S")
        ## Process other files and directories

    def _readPlist(self, filen) :
        if filen in self.dtree :
            plist = Uplist(font = self, filen = filen)
            self.dtree[filen].setinfo(read = True, fileObject = plist, fileType = "xml")
            return plist
        else :
            self.logger.log( filen + " does not exist", "S")

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
            odtree = UT.dirTree(outdir)
        else :
            if not os.path.exists(outdir) : # If outdir does not exist, create it
                try:
                    os.mkdir(outdir)
                except Exception as e :
                    print e
                    sys.exit(1)
                odtree = {}
            else:
                if not os.path.isdir(outdir) : self.logger.log( outdir + " not a directory", "S")
                dirlist = os.listdir(outdir)
                if dirlist == [] : # Outdir is empty
                    odtree = {}
                elif "metainfo.plist" in dirlist :
                    self.logger.log("Output UFO already exists - reading for comparison", "P")
                    odtree = UT.dirTree(outdir)
                else:
                    self.logger.log( outdir + " exists but is not a UFO", "S")
        # Update version info etc
        UFOversion = self.outparams["UFOversion"]
        self.metainfo["formatVersion"][1].text = str(UFOversion)
        self.metainfo["creator"][1].text = "org.sil.scripts.pysilfont"

        # Set standard UFO files for output
        dtree = self.dtree
        setFileForOutput(dtree, "metainfo.plist", self.metainfo, "xml")
        if "fontinfo" in self.__dict__ : setFileForOutput(dtree, "fontinfo.plist", self.fontinfo,  "xml")
        if "groups" in self.__dict__ : setFileForOutput(dtree, "groups.plist", self.groups, "xml")
        if "kerning" in self.__dict__ : setFileForOutput(dtree, "kerning.plist", self.kerning, "xml")
        if "lib" in self.__dict__ : setFileForOutput(dtree, "lib.plist", self.lib, "xml")
        if UFOversion == "3" : setFileForOutput(dtree, "layercontents.plist", self.layercontents, "xml")
        if "features" in self.__dict__ : setFileForOutput(dtree, "features.fea", self.features, "text")
        # Set glyph layers for output
        for layer in self.layers : layer.setForOutput()

        # Write files to disk

        self.logger.log("Writing font to " + outdir, "P")

        writeToDisk(dtree, outdir, self, odtree,)
        self.logger.log("All done!", "P") ## Just for timing tests

class Ulayer(_Ucontainer) :

    def __init__(self, layername, layerdir, font) :
        self._contents = {}
        self.dtree = font.dtree.subTree(layerdir)
        font.dtree[layerdir].read = True
        self.layername = layername
        self.layerdir = layerdir
        self.font = font
        fulldir = os.path.join(font.ufodir,layerdir)
        self.contents = Uplist( font = font, dirn = fulldir, filen = "contents.plist" )
        self.dtree["contents.plist"].setinfo(read = True, fileObject = self.contents, fileType = "xml")

        if font.UFOversion == "3" :
            if 'layerinfo.plist' in self.dtree :
                self.layerinfo = Uplist( font = font, dirn = fulldir, filen = "layerinfo.plist" )
                self.dtree["layerinfo.plist"].setinfo(read = True, fileObject = self.layerinfo, fileType = "xml")

        for glyphn in sorted(self.contents.keys()) :
            glifn = self.contents[glyphn][1].text
            if glifn in self.dtree :
                glyph = Uglif(layer = self, filen = glifn)
                self._contents[glyphn] = glyph
                self.dtree[glifn].setinfo( read = True, fileObject = glyph, fileType = "xml")
                if glyph.name <> glyphn :
                    super(Uglif,glyph).__setattr__("name",glyphn) # Need to use super to bypass normal glyph renaming logic
                    self.font.logger.log( "Glyph names in glif and contents.plist did not match for " + glyphn + "; corrected", "W")
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
        self.dtree.removedfiles[glyph.filen] = newname # Track so original glif does not get reported as invalid
        glyph.filen = newname
        self.contents[glyphn][1].text = newname

    def addGlyph(self,glyph) :
        glyphn = glyph.name
        if glyphn in self._contents : self.font.logger.log(glyphn + " already in font", "X")
        self._contents[glyphn] = glyph
        # Set glif name
        glifn = makeFileName(glyphn)
        names = []
        while glifn in self.contents : # need to check for duplicate glif names
            names.append(glfin)
            glifn = makeFileName(glyphn, names)
        glifn += ".glif"
        glyph.filen = glifn
        # Add to contents.plist and dtree
        self.contents.addval(glyphn,"string",glifn)
        self.dtree[glifn] = UT.dirTreeItem(read = False, added = True, fileObject = glyph, fileType = "xml")

    def delGlyph(self,glyphn) :
        self.dtree.removedfiles[self[glyphn].filen] = "deleted" # Track so original glif does not get reported as invalid
        del self._contents[glyphn]
        self.contents.remove(glyphn)

class Uplist(ETU.xmlitem, _plist) :

    def __init__(self, font = None, dirn = None, filen = None, parse = True) :
        if dirn is None and font: dirn = font.ufodir
        ETU.xmlitem.__init__(self, dirn, filen, parse)
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

class Uglif(ETU.xmlitem) :
    # Unlike plists, glifs can have multiples of some sub-elements (eg anchors) so create lists for those

    def __init__(self, layer, filen = None, parse = True, name = None, format = None) :
        dirn = os.path.join(layer.font.ufodir, layer.layerdir)
        ETU.xmlitem.__init__(self, dirn, filen, parse) # Will read item from file if dirn and filen both present
        self.type="glif"
        self.layer = layer
        self.format = format if format else '2'
        self.name = name
        self.outparams = None
        self.glifElemOrder = self.layer.font.outparams["glifElemOrder"]
        # Set initial values for sub-objects
        for elem in self.glifElemOrder :
            if elem in _glifElemMulti :
                self._contents[elem] = []
            else :
                self._contents[elem] = None
        if self.etree is not None : self.process_etree()

    def __setattr__(self, name, value) :
        if name == "name" and getattr(self,"name",None): # Existing glyph name is being changed
            oname = self.name
            if value in self.layer._contents : self.layer.font.logger.log(name + " already in font", "X")
            # Update the _contents disctionary
            del self.layer._contents[oname]
            self.layer._contents[value] = self
            # Set glif name
            glifn = makeFileName(value)
            names = []
            while glifn in self.layer.contents : # need to check for duplicate glif names
                names.append(glfin)
                glifn = makeFileName(value, names)
            glifn += ".glif"

            # Update to contents.plist, filen and dtree
            self.layer.contents.remove(oname)
            self.layer.contents.addval(value,"string",glifn)
            self.layer.dtree.removedfiles[self.filen] = glifn # Track so original glif does not get reported as invalid
            self.filen = glifn
            self.layer.dtree[glifn] = UT.dirTreeItem(read = False, added = True, fileObject = self, fileType = "xml")
        super(Uglif,self).__setattr__(name,value)

    def process_etree(self) :
        et = self.etree
        self.name = getattrib(et,"name")
        self.format = getattrib(et,"format")
        if self.format is None :
            if self.layer.font.UFOversion == "3" :
                self.format = '2'
            else :
                self.format = '1'
        for i in range(len(et)) :
            element = et[i]
            tag = element.tag
            if not tag in self.glifElemOrder : self.layer.font.logger.log("Invalid element "+tag+" in glif "+self.name, "E")
            if tag in _glifElemF1 or self.format == '2' :
                if tag in _glifElemMulti :
                    self._contents[tag].append(self.makeObject(tag,element))
                else:
                    self._contents[tag] = self.makeObject(tag,element)

        # Convert UFO2 style anchors to UFO3 anchors
        if self._contents['outline'] is not None and self.format == "1":
            for contour in self._contents['outline'].contours[:] :
                if contour.UFO2anchor :
                    del contour.UFO2anchor["type"] # remove type="move"
                    self.add('anchor',contour.UFO2anchor)
                    self._contents['outline'].removeobject(contour, "contour")

        self.format = "2"

    def rebuildET(self) :
        self.etree = ET.Element("glyph")
        et = self.etree
        et.attrib["name"] = self.name
        et.attrib["format"] = self.format
        # Insert sub-elements
        for elem in self.glifElemOrder :
            if elem in _glifElemF1 or self.format == "2" : # Check element is valid for glif format
                item = self._contents[elem]
                if item is not None :
                    if elem in _glifElemMulti :
                        for object in item :
                            et.append(object.element)
                    else :
                        et.append(item.element)

    def add(self,ename,attrib = None) :
        # Add an element and corrensponding object to a glif
        element = ET.Element(ename)
        if attrib : element.attrib = attrib
        if ename == "lib" : ET.SubElement(element,"dict")
        multi = True if ename in _glifElemMulti else False

        # Check element does not already exist for single elements
        if self._contents[ename] and not multi : self.layer.font.logger.log( "Already an " + enam + "in glif", "X")

        # Add new object
        if multi :
            self._contents[ename].append(self.makeObject(ename,element))
        else:
            self._contents[ename] = self.makeObject(ename,element)

    def remove(self, ename, index = None, object = None ) :
        # Remove object from a glif
        # For multi objects, an index or object must be supplied to identify which
        # to delete
        if ename in _glifElemMulti :
            item = self._contents[ename]
            if index is None : index = item.index(object)
            del item[index]
        else :
            self._contents[ename] = None

    def convertToFormat1(self) :
        # Convert to a glif format of 1 (for UFO2) prior to writing out
        self.format = "1"
        # Change anchors to UFO2 style anchors.  Sort anchors by anchor name first
        anchororder = sorted(self._contents['anchor'], key=lambda x: x.element.attrib['name'])
        for anchor in anchororder :
            element = anchor.element
            for attrn in ('colour', 'indentifier') : # Remove format 2 attributes
                if attrn in element.attrib : del element.attrib[attrn]
            element.attrib['type'] = 'move'
            contelement = ET.Element("contour")
            contelement.append(ET.Element("point",element.attrib))
            self._contents['outline'].appendobject(Ucontour(self._contents['outline'],contelement),"contour")
            self.remove('anchor',object=anchor)

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
        self.glif = glif
        if 'width' in element.attrib :
            self.width = element.attrib[str('width')]
        else :
            self.width = None
        if 'height' in element.attrib :
            self.height = element.attrib[str('height')]
        else :
            self.height = None

    def __setattr__(self, name, value) :
        if name in ('width', 'height') and value is not None:
            value = str(value)
            self.element.attrib[name] = value
        super(Uadvance,self).__setattr__(name,value)

class Uunicode(Uelement) :

    def __init__(self, glif, element) :
        super(Uunicode,self).__init__(element)
        self.glif = glif
        if 'hex' in element.attrib :
            self.hex = element.attrib['hex']
        else :
            self.hex = ""
            self.glif.logger.log("No unicode hex attribute for " + glif.name, "E")

    def __setattr__(self, name, value) :
        if name == "hex" : self.element.attrib['hex'] = value
        super(Uunicode,self).__setattr__(name,value)

class Unote(Uelement) :

    def __init__(self, glif, element) :
        self.glif = glif
        super(Unote,self).__init__(element)

class Uimage(Uelement) :

    def __init__(self, glif, element) :
        self.glif = glif
        super(Uimage,self).__init__(element)

class Uguideline(Uelement) :

    def __init__(self, glif, element) :
        self.glif = glif
        super(Uguideline,self).__init__(element)

class Uanchor(Uelement) :

    def __init__(self, glif, element) :
        self.glif = glif
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

class Ulib(_Ucontainer, _plist) :
    # For glif lib elements; top-level lib files use Uplist
    def __init__(self, glif, element) :
        self.glif = glif
        self.element = element # needs both element and etree fo compatibility
        self.etree = element   # with other glif components and _plist methods
        self._contents = {}
        self.reindex()

    def reindex(self) :
        self._contents.clear() # Clear existing contents, if any
        pl = self.element[0]
        if pl.tag == "dict" :
            for i in range(0,len(pl),2):
                key = pl[i].text
                self._contents[key] = [pl[i],pl[i+1]] # The two elements for the item

class UfeatureFile(UtextFile) :

    def __init__(self, font, dirn, filen) :
        super(UfeatureFile,self).__init__(font,dirn,filen)

def writeXMLobject(dtreeitem, font, dirn, filen, exists) :
    params = font.outparams

    object = dtreeitem.fileObject
    if object.outparams : params = object.outparams # override default params with object-specific ones
    indentFirst = params["indentFirst"]
    attribOrder = {}
    if object.type in params['attribOrders'] : attribOrder = params['attribOrders'][object.type]
    if object.type == "plist" :
        indentFirst = params["plistIndentFirst"]
        object.etree.attrib[".doctype"] = 'plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"'

    # Format ET data if any data parameters are set
    if params["sortDicts"] or params["precision"] is not None : normETdata(object.etree, params, type = object.type)

    etw = ETU.ETWriter(object.etree, attributeOrder = attribOrder, indentIncr = params["indentIncr"],
        indentFirst = indentFirst, indentML = params["indentML"], precision = params["precision"], numAttribs = params["numAttribs"])
    etw.serialize_xml(object.write_to_xml)
    # Now we have the output xml, need to compare with existing item's xml, if present
    changed = True

    if exists: # File already on disk
        if exists == "same" : # Output and input locations the same
            oxmlstr = object.inxmlstr
        else: # Read existing XML from disk
            oxmlstr=""
            try :
                oxml=open(os.path.join( dirn, filen), "r")
            except Exception as e :
                print e
                sys.exit(1)
            for line in oxml.readlines() :
                oxmlstr += line
            oxml.close()
        if oxmlstr == object.outxmlstr : changed = False

    if changed : object.write_to_file(dirn,filen)
    dtreeitem.written = True # Mark as True, even if not changed - the file should still be there!

def setFileForOutput(dtree, filen, fileObject, fileType) : # Put details in dtree, creating item if needed
    if not filen in dtree :
        dtree[filen] = UT.dirTreeItem()
        dtree[filen].added = True
    dtree[filen].setinfo(fileObject = fileObject, fileType = fileType, towrite = True)

def writeToDisk(dtree, outdir, font, odtree = {}, logindent = "") :

    # Make lists of items in dtree and odtree with type prepended for sorting and comparison purposes
    dtreelist = []
    for filen in dtree : dtreelist.append(dtree[filen].type+filen)
    dtreelist.sort()

    odtreelist = []
    if odtree == {} :
        locationtype = "Empty"
    else:
        if outdir == font.ufodir :
            locationtype = "Same"
        else :
            locationtype = "Different"
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
                logmess = 'Deleting '+ ofilen + ' from existing output UFO'
                os.remove(os.path.join(outdir,ofilen))
            else:
                logmess = 'Deleting directory '+ ofilen + ' from existing output UFO'
                shutil.rmtree(os.path.join(outdir,ofilen))
            if ofilen not in dtree.removedfiles : font.logger.log(logmess, "W") # No need to log warning for remaned files
            okey = odtreelist.pop(0) if odtreelist <> [] else None

        if key == okey :
            exists = locationtype
            okey = odtreelist.pop(0) if odtreelist <> [] else None # Ready for next loop
        else :
            exists = False

        if dtreeitem.type == "f" :
            if dtreeitem.towrite :
                font.logger.log(logindent + filen, "V")
                if dtreeitem.fileType == "xml" :
                    if dtreeitem.fileObject : # Only write if object has items
                        if dtreeitem.fileObject.type == "glif" : # Delete lib if no items in it
                            glif = dtreeitem.fileObject
                            if glif["lib"] is not None :
                                if glif["lib"].__len__() == 0 :
                                    glif.remove("lib")
                            glif.rebuildET()
                        writeXMLobject(dtreeitem,font,outdir, filen, exists)
                    else : # Delete existing item if the current object is empty
                        if exists :
                            font.logger.log('Deleting empty item '+ filen + ' from existing output UFO', "I")
                            os.remove(os.path.join(outdir,filen))
                elif dtreeitem.fileType == "text" :
                    dtreeitem.fileObject.write(dtreeitem, outdir, filen, exists)
                    ## Need to add code for other file types
            else :
                if filen in dtree.removedfiles :
                    if exists :
                        os.remove(os.path.join(outdir,filen)) # Silently remove old file for renamed files
                        exists = False
                else : # File should not have been in original UFO
                    if exists == "same" :
                        font.logger.log('Deleting '+ filen + ' from existing UFO', "W")
                        os.remove(os.path.join(outdir,filen))
                        exists = False
                    else :
                        if not dtreeitem.added : font.logger.log('Skipping invalid file '+ filen + ' from input UFO', "W")
                if exists:
                    font.logger.log('Deleting '+ filen + ' from existing output UFO', "W")
                    os.remove(os.path.join(outdir,filen))

        else : # Must be directory
            if not dtreeitem.read :
                font.logger.log(logindent + "Skipping invalid input directory " + filen,"W")
                if exists :
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

            if exists :
                subodtree = odtree[filen].dirtree
            else :
                subodtree = {}
            subindent = logindent + "  "
            writeToDisk(dtreeitem.dirtree, subdir, font, subodtree, subindent)
            if os.listdir(subdir) == [] : os.rmdir(subdir) # Delete directory if empty

    while okey: # Any remaining items in odree list are no longer needed
        ofilen = okey[1:]
        if okey[0:1] == "f" :
            logmess = 'Deleting '+ ofilen + ' from existing output UFO'
            os.remove(os.path.join(outdir,ofilen))
        else:
            logmess = 'Deleting directory '+ ofilen + ' from existing output UFO', "W"
            shutil.rmtree(os.path.join(outdir,ofilen))
        if ofilen not in dtree.removedfiles : font.logger.log(logmess, "W") # No need to log warning for removed files
        okey = odtreelist.pop(0) if odtreelist <> [] else None

def normETdata(element, params, type) :
    # Recursively normalise the data an an ElementTree element
    for subelem in element :
        normETdata(subelem, params, type)

    precision = params["precision"]
    if precision is not None:
        if element.tag in ("integer","real"):
            num = round(float(element.text),precision)
            if num ==int(num) :
                element.tag = "integer"
                element.text = "{}".format(int(num))
            else :
                element.tag = "real"
                element.text = "{}".format(num)

    if params["sortDicts"] and element.tag == "dict" :
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

def getattrib(element,attrib) : return element.attrib[attrib] if attrib in element.attrib else None

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
