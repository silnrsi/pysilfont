# SAX handler class
# Create a dictionary representing the supplemental glyph info.
# The keys are SILNms (glyph name attribute)
# The values are objects with attributes
# The object attributes are based on either xml element attributes or xml element characters
#   Object attributes that mirror xml attributes are named like element_attribute and contain the xml attr value
#     If an attribute doesn't exist in the xml, no object attribute will exist either
#   Object attributes that mirror xml element characters are named based on the xml element and contain the characters
# Duplicate glyph name attributes are detected
# To debug assertions, run (not import) the calling script in PythonWin
#   with Debugging set to Post-Mortem of unhandled exceptions. This should cause a break at the assertion.
#   Also open the watch window to display the value of the data causing the assertion.

###boilder plate code for using the classes
##import xml.sax
##import XmlFL
##
##glyph_supp_fn = r"C:\Roman Font\glyph_supp.xml"
##fl_xml_fn = r"C:\Roman Font\SILDLRG-0235.xml"
##
###parse glyph supplemental info file    
##parser = xml.sax.make_parser()
##handler = XmlFL.CollectXmlInfo()
##parser.setContentHandler(handler)
##parser.parse(glyph_supp_fn)
##glyph_supp_dict = handler.get_data_dict()
##
###parse XML dump of FL file
##handler = XmlFL.CollectFlNameUsvInfo()
##parser.setContentHandler(handler)
##parser.parse(fl_xml_fn)
##fl_nm_usv_dict = handler.get_fl_xml_dict()

import xml.sax.handler

class CollectXmlInfo(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.data_dict = {}
        self.dict_key = None
        self.data = None
        self.char_capture_state = None
        self.char_capture_element = None

    def get_data_dict(self):
        return self.data_dict.copy()

    #private method
    def save_attrs(self, attrs, prefix = None):
        "creates attributes on glyph named according to the keys in attrs"
        assert(self.data)
        for key in attrs.keys():
            if prefix:
                t_key = prefix + "_" + key
            else:
                t_key = key
            setattr(self.data, t_key, attrs[key])

    #override standard SAX handler methods
            
    def startElement(self, name, attrs):
        if name == "glyph":
            #this element contains the others, so must do initialization
            assert(not self.data)
            self.data = NullClass()
            
            self.save_attrs(attrs, name)
            
            #the dict_key can be set elsewhere
            #but must be done before it is needed
            assert(attrs["name"])
            self.dict_key = attrs["name"] #save before potential assert failure for debugging
            if self.data_dict.has_key(attrs["name"]): #verify glyph names are unique
                print "duplicate glyph name: %s" % self.dict_key
                assert(0) 
        elif name == "ps_name":
            self.save_attrs(attrs, name)
        elif name == "feature":
            self.save_attrs(attrs, name)
        elif name == "var_uid":
            self.char_capture_state = 1
            self.char_capture_element = name
        elif name == "lig_uids":
            self.char_capture_state = 1
            self.char_capture_element = name
        else: #don't store composite or its sub-elements
            pass

    def endElement(self, name):
        if name == "glyph":
            #this element contains the others, so must store data and clean up
            self.data_dict[self.dict_key] = self.data
            self.dict_key = None
            self.data = None
        elif name == "var_uid":
            self.char_capture_state = 0
            self.char_capture_element = None
        elif name == "lig_uids":
            self.char_capture_state = 0
            self.char_capture_element = None
                
    def characters(self, str):
        if not isinstance(self, CollectXmlInfo):
            return
        if self.char_capture_state:
            if hasattr(self.data, self.char_capture_element):
                s = getattr(self.data, self.char_capture_element)
                setattr(self.data, self.char_capture_element, s + str.rstrip())
            else:
                setattr(self.data, self.char_capture_element, str.rstrip())
        else:
            return

class NullClass: #used to hold dynamically created attributes
    pass        

class CollectFlNameUsvInfo(xml.sax.handler.ContentHandler):
    #create a mapping with SILNm as key and USV as value (could be None)
    def __init__(self):
        self.fl_nm_usv_dict = {}

    def get_fl_xml_dict(self):
        return self.fl_nm_usv_dict.copy()

    def startElement(self, name, attrs):
        if name == "glyph":
            glyph_nm = None
            if attrs.has_key("PSName"):
                glyph_nm = attrs["PSName"]
                self.fl_nm_usv_dict[glyph_nm] = None
            else:
                print "FL glyph missing PSName"
                assert(0)
            if attrs.has_key("UID"):
                 self.fl_nm_usv_dict[glyph_nm] = attrs["UID"]

class CollectFlNameGidInfo(xml.sax.handler.ContentHandler):
    #create a mapping with SILNm as key and glyph id as value (could be None)
    def __init__(self):
        self.fl_nm_gid_dict = {}

    def get_fl_xml_dict(self):
        return self.fl_nm_gid_dict.copy()

    def startElement(self, name, attrs):
        if name == "glyph":
            glyph_nm = None
            if attrs.has_key("PSName"):
                glyph_nm = attrs["PSName"]
                self.fl_nm_gid_dict[glyph_nm] = None
            else:
                print "FL glyph missing PSName"
                assert(0)
            if attrs.has_key("GID"):
                 self.fl_nm_gid_dict[glyph_nm] = attrs["GID"]
            else:
                print "FL glyph missing GID"
                assert(0)

class CollectFlNameApInfo(xml.sax.handler.ContentHandler):
    #create a mapping with SILNm as key and list of AP names as value (could be None)
    def __init__(self):
        self.fl_nm_ap_dict = {}
        self.glyph_nm, self.ap_lst = None, None

    def get_fl_xml_dict(self):
        return self.fl_nm_ap_dict.copy()

    def startElement(self, name, attrs):
        if name == "glyph":
            if attrs.has_key("PSName"):
                self.glyph_nm = attrs["PSName"]
                self.fl_nm_ap_dict[self.glyph_nm] = None
            else:
                print "FL glyph missing PSName"
                assert(0)
            self.ap_lst = []
        if name == "point":
            if attrs.has_key("type"):
                self.ap_lst.append(attrs["type"])
            else:
                print "FL point missing type"
                assert(0)
        
    def endElement(self, name):
        if name == "glyph":
            self.fl_nm_ap_dict[self.glyph_nm] = self.ap_lst
            self.glyph_nm, self.ap_lst = None, None

class CollectFlNameApDetailInfo(xml.sax.handler.ContentHandler):
    #create a mapping with SILNm as key and list of tuples containing AP data as value (could be None)
    def __init__(self):
        self.fl_nm_apinfo_dict = {}
        self.glyph_nm, self.apinfo, self.apinfo_lst = None, None, None

    def get_fl_xml_dict(self):
        return self.fl_nm_apinfo_dict.copy()

    def startElement(self, name, attrs):
        if name == "glyph":
            if attrs.has_key("PSName"):
                self.glyph_nm = attrs["PSName"]
                self.fl_nm_apinfo_dict[self.glyph_nm] = None
            else:
                print "FL glyph missing PSName"
                assert(0)
            self.apinfo, self.apinfo_lst = [], []
        if name == "point":
            if attrs.has_key("type"):
                self.apinfo.append(attrs["type"])
            else:
                print "FL point missing type"
                assert(0)
            if attrs.has_key("mark"):
                self.apinfo.append(attrs["mark"])
            else:
                print "FL point missing mark"
                assert(0)
        if name == "location":
            if attrs.has_key("x"):
                self.apinfo.append(attrs["x"])
            else:
                print "FL point position missing x"
                assert(0)
            if attrs.has_key("y"):
                self.apinfo.append(attrs["y"])
            else:
                print "FL point position missing y"
                assert(0)
        
    def endElement(self, name):
        if name == "glyph":
            self.fl_nm_apinfo_dict[self.glyph_nm] = self.apinfo_lst
            self.glyph_nm, self.apinfo, self.apinfo_lst = None, None, None
        if name == "point":
            assert(len(self.apinfo) == 4)
            self.apinfo_lst.append(self.apinfo)
            self.apinfo = []

class CollectFlNameComponentInfo(xml.sax.handler.ContentHandler):
    #create a mapping with SILNm as key and list of components as value (could be None)
    def __init__(self):
        self.fl_nm_component_dict = {}
        self.glyph_nm, self.component_lst = None, None

    def get_fl_xml_dict(self):
        return self.fl_nm_component_dict.copy()

    def startElement(self, name, attrs):
        if name == "glyph":
            if attrs.has_key("PSName"):
                self.glyph_nm = attrs["PSName"]
                self.fl_nm_component_dict[self.glyph_nm] = None
            else:
                print "FL glyph missing PSName"
                assert(0)
            self.component_lst = []
        if name == "compound":
            if attrs.has_key("PSName"):
                self.component_lst.append(attrs["PSName"])
            else:
                print "FL compound missing PSName"
                assert(0)
        
    def endElement(self, name):
        if name == "glyph":
            self.fl_nm_component_dict[self.glyph_nm] = self.component_lst
            self.glyph_nm, self.ap_lst = None, None

#probably superceded by CollectFlNameComponentInfo
class CollectFlComponentInfo(xml.sax.handler.ContentHandler):
    "collect a dictionary of all component glyphs with their frequency"
    def __init__(self):
        self.component_dict = {}

    def get_component_lst(self):
        "return a list of components"
        return self.component_dict.keys()

    def startElement(self, name, attrs):
        if name == "compound":
            name = attrs["PSName"].encode()
            try:
                self.component_dict[name] += 1
            except:
                self.component_dict[name] = 1
