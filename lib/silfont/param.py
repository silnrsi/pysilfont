#!/usr/bin/env python
'Parameter handling for use in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2016, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '1.0.0'

import silfont.util as UT
import ConfigParser

# Default parameters for use in pysilfont modules
#   Names must be case-insensitively unique across all parameter classes
#   Parameter types are deduced from the default values

# Default parameters for all modules
defparams = {}
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
    "UFOversion":       "",   # UFOversion - defaults to existing unless a value is supplied
    "glifElemOrder":    ['advance', 'unicode', 'note',   'image',  'guideline', 'anchor', 'outline', 'lib'], # Order to output glif elements
    "numAttribs":       ['pos', 'width', 'height', 'xScale', 'xyScale', 'yxScale', 'yScale', 'xOffset', 'yOffset', 'x', 'y', 'angle', 'format'],    # Used with precision above
    "attribOrders.glif":[ 'pos', 'width', 'height', 'fileName', 'base', 'xScale', 'xyScale', 'yxScale', 'yScale',
                'xOffset', 'yOffset', 'x', 'y', 'angle', 'type', 'smooth', 'name', 'format', 'color', 'identifier']
    }

class params(object) :
    # Object for holding parameters information, organised by class (eg logging)
    def __init__(self) :
        self.classes = {} # Dictionary containing a list of parameters in each class
        self.paramclass = {} # Dictionary of class name for each parameter name
        self.types = {} # Python type for each parameter deduced from initial values supplied
        self.listtypes = {} # If type is dict, the type of values in the dict
        self.logger = UT.loggerobj()
        self.sets = {"default": _paramset(self, "default", "defaults")}
        self.lcase = {} # Lower case index ot parameters names
        for classn in defparams :
            self.classes[classn] = []
            for parn in defparams[classn] :
                value = defparams[classn][parn]
                self.classes[classn].append(parn)
                self.paramclass[parn] = classn
                self.types[parn] = type(value)
                if type(value) is list : self.listtypes[parn] = type(value[0])
                self.sets["default"][parn] = value
                self.lcase[parn.lower()] = parn

    def addset(self, name, sourcedesc = None, inputdict = None, configfile = None, copyset = None, updatewith = []) :
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
        if type(updatewith) is not list : updatewith = [updatewith]
        for update in updatewith : self.sets[name].updatewith(update)

class _paramset(dict) :
    # Set of parameter values
    def __init__(self, params, name, sourcedesc, inputdict = {}) :
        self.name = name
        self.sourcedesc = sourcedesc # Description of source for reporting
        self.params = params # Parent paraminfo object
        for parn in inputdict : self.add(parn,inputdict[parn])

    def add(self,parn,value) :
        parn = self.params.lcase[parn.lower()]
        if parn not in self.params.sets["default"] :
            self.params.logger.log("Invalid parameter " + parn + " from " + self.sourcedesc, "S")
        ptyp = self.params.types[parn]
        if ptyp is list and type(value) is not list :value = value.split(",") # Convert csv string into list
        if ptyp is bool : value = UT.str2bool(value)
        if ptyp is list :
            if len(value) < 2 : self.logger.log (paramsource+" parameter "+parn+" must have a list of values: "+newpars[parn],"S")
            valuesOK = True
            listtype = self.params.listtypes[parn]
            for i,val in enumerate(value) :
                if listtype is bool :
                    val = str2bool(val)
                    value[i] = val
                if type(val) <> listtype : valuesOK = False
            if not valuesOK : self.logger.log ("Invalid "+paramsource+" parameter type for "+parn+": "+params.types[parn],"S")
        self[parn] = value ### Need to validate types, including within lists

    def updatewith(self,update) :
        # Update a set with values from another set
        for parn in self.params.sets[update] : self[parn] = self.params.sets[update][parn] ### Log changes in values



'''for (paramsource,newpars) in (("Config file",cfgparams),("lib.plist",libparams),("Command-line",clparams)):
            if newpars :
                for parn in newpars :
                    if parn not in params: self.logger.log ("Invalid "+paramsource+" parameter: "+parn,"S")
                    if parn in params.groups["outparams"] : # only parameters relevant to a font
                        ptyp = params.types[parn]
                        value = newpars[parn]
                        if ptyp is list : value = value.split(",") # Convert csv string into list
                        if ptyp is bool : value = str2bool(value)
                        if type(value) <> ptyp :
                            if param == "UFOversion" : # Default is None, so type does not match if value given
                                if value not in ("2","3") : self.logger.log ("UFO version must be 2 or 3","S")
                            else:
                                self.logger.log ("Invalid "+paramsource+" parameter type for "+parn+": "+newpars[parn],"S")
                        if ptyp is list :
                            if len(value) < 2 : self.logger.log (paramsource+" parameter "+parn+" must have a list of values: "+newpars[parn],"S")
                            valuesOK = True
                            listtype = params.listtypes[parn]
                            for i,val in enumerate(value) :
                                if listtype is bool :
                                    val = str2bool(val)
                                    value[i] = val
                                if type(val) <> listtype : valuesOK = False
                            if not valuesOK : self.logger.log ("Invalid "+paramsource+" parameter type for "+parn+": "+params.types[parn],"S")
                        currentval = params[parn]
                        if value <> currentval :
                            if parn == "glifElemOrder" : # Must be the standard elements with just the order changed
                                if sorted(value) <> sorted(currentval) : self.logger.log("Invalid "+paramsource+ " values for glifElemOrder", "S")
                            old = str(currentval)
                            new = str(value)
                            if old <> old.strip() or new <> new.strip() : # Add quotes if there are leading or trailing spaces
                                old = '"'+old+'"'
                                new = '"'+new+'"'
                            self.logger.log(paramsource + " parameters: changing "+parn+" from " + old  + " to " + new,"I")
                            params[parn] = value'''