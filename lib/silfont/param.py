#!/usr/bin/env python
'Parameter handling for use in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '1.1.0'

import silfont.util as UT
import ConfigParser

# Default parameters for use in pysilfont modules
#   Names must be case-insensitively unique across all parameter classes
#   Parameter types are deduced from the default values

# Default parameters for all modules
defparams = {}
defparams['main']   = {'version' : __version__, 'copyright' : __copyright__}
defparams['logging']   = {'scrlevel': 'P', 'loglevel': 'W'}
defparams['backups']   = {'backup': True, 'backupdir': 'backups', 'backupkeep': 5}
# Default parameters for UFO module
defparams['outparams'] = {
    "indentIncr":       "  ",   # XML Indent increment
    "indentFirst":      "  ",   # First XML indent
    "indentML":         False,  # Should multi-line string values be indented?
    "plistIndentFirst": "",     # First indent amoutn for plists
    "sortDicts":        True,   # Should dict elements be sorted alphabetically?
    'precision':        6,      # Decimal precision to use in XML output - both for real values and for attributes if numeric
    "renameGlifs":      True,   # Rename glifs based on UFO3 suggested algorithm
    "UFOversion":       "",     # UFOversion - defaults to existing unless a value is supplied
    "glifElemOrder":    ['advance', 'unicode', 'note',   'image',  'guideline', 'anchor', 'outline', 'lib'], # Order to output glif elements
    "numAttribs":       ['pos', 'width', 'height', 'xScale', 'xyScale', 'yxScale', 'yScale', 'xOffset', 'yOffset', 'x', 'y', 'angle', 'format'],    # Used with precision above
    "attribOrders.glif":[ 'pos', 'width', 'height', 'fileName', 'base', 'xScale', 'xyScale', 'yxScale', 'yScale', 'xOffset', 'yOffset',
                          'x', 'y', 'angle', 'type', 'smooth', 'name', 'format', 'color', 'identifier']
    }

class params(object) :
    # Object for holding parameters information, organised by class (eg logging)
    def __init__(self) :
        self.classes = {} # Dictionary containing a list of parameters in each class
        self.paramclass = {} # Dictionary of class name for each parameter name
        self.types = {} # Python type for each parameter deduced from initial values supplied
        self.listtypes = {} # If type is dict, the type of values in the dict
        self.logger = UT.loggerobj()
        defset = _paramset(self, "default", "defaults")
        self.sets = {"default": defset}
        self.lcase = {} # Lower case index of parameters names
        for classn in defparams :
            self.classes[classn] = []
            for parn in defparams[classn] :
                value = defparams[classn][parn]
                self.classes[classn].append(parn)
                self.paramclass[parn] = classn
                self.types[parn] = type(value)
                if type(value) is list : self.listtypes[parn] = type(value[0])
                super(_paramset,defset).__setitem__(parn,value) # __setitem__ in paramset does not allow new values!
                self.lcase[parn.lower()] = parn

    def addset(self, name, sourcedesc = None, inputdict = None, configfile = None, copyset = None) :
        # Create a subset from one of a dict, config file or existing set
        # Only one option should used per call
        # sourcedesc should be added for user-supplied data (eg config file) for reporting purposes
        dict = {}
        if configfile :
            config = ConfigParser.ConfigParser()
            config.readfp(open(configfile))
            if sourcedesc is None : sourcedesc = configfile
            for classn in config.sections() :
                for item in config.items(classn) :
                    parn = item[0]
                    val =  item[1].strip('"').strip("'")
                    dict[parn] = val
        elif copyset :
            if sourcedesc is None : sourcedesc = "Copy of " + copyset
            for parn in self.sets[copyset] :
                dict[parn] = self.sets[copyset][parn]
        elif inputdict:
            dict = inputdict
        if sourcedesc is None : sourcedesc = "unspecified source"
        self.sets[name] = _paramset(self, name, sourcedesc, dict)

class _paramset(dict) :
    # Set of parameter values
    def __init__(self, params, name, sourcedesc, inputdict = {}) :
        self.name = name
        self.sourcedesc = sourcedesc # Description of source for reporting
        self.params = params # Parent paraminfo object
        for parn in inputdict : self[parn] = inputdict[parn]

    def __setitem__(self, parn, value) :
        origvalue=value
        origparn=parn
        parn = parn.lower()
        if parn not in self.params.lcase :
            self.params.logger.log("Invalid parameter " + origparn + " from " + self.sourcedesc, "S")
        else :
            parn = self.params.lcase[parn]
        ptyp = self.params.types[parn]
        if ptyp is bool :
            value = UT.str2bool(value)
            if value is None : self.params.logger.log (self.sourcedesc+" parameter "+origparn+" must be boolean: " + origvalue,"S")
        if ptyp is list :
            if type(value) is not list : value = value.split(",") # Convert csv string into list
            if len(value) < 2 : self.params.logger.log (self.sourcedesc+" parameter "+origparn+" must have a list of values: " + origvalue,"S")
            valuesOK = True
            listtype = self.params.listtypes[parn]
            for i,val in enumerate(value) :
                if listtype is bool :
                    val = str2bool(val)
                    if val is None : self.params.logger.log (self.sourcedesc+" parameter "+origparn+" must contain boolean values: " + origvalue,"S")
                    value[i] = val
                if type(val) <> listtype : valuesOK = False
            if not valuesOK : self.logger.log ("Invalid "+paramsource+" parameter type for "+origparn+": "+self.params.types[parn],"S")
        if parn in ("loglevel", "scrlevel") : # Need to check log level is valid before setting it since otherwise logging will fail
            value = value.upper()
            if value not in self.params.logger.loglevels : self.params.logger.log (self.sourcedesc+" parameter "+parn+" invalid","S")
        super(_paramset,self).__setitem__(parn,value)

    def updatewith(self,update, sourcedesc = None, log = True) :
        # Update a set with values from another set
        if sourcedesc is None : sourcedesc = self.params.sets[update].sourcedesc
        for parn in self.params.sets[update] :
            oldval = self[parn] if parn in self else ""
            self[parn] = self.params.sets[update][parn]
            if log and oldval <> "" and self[parn] <> oldval :
                old = str(oldval)
                new = str(self[parn])
                if old <> old.strip() or new <> new.strip() : # Add quotes if there are leading or trailing spaces
                    old = '"'+old+'"'
                    new = '"'+new+'"'
                self.params.logger.log(sourcedesc + " parameters: changing "+parn+" from " + old  + " to " + new,"I")
