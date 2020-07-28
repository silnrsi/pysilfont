#!/usr/bin/env python
'General classes and functions for use in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014-2020 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'

from glob import glob
from collections import OrderedDict
import sys, os, argparse, datetime, shutil, csv, codecs, io
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import silfont

class loggerobj(object):
    # For handling log messages.
    # Use S for severe errors caused by data, parameters supplied by user etc
    # Use X for severe errors caused by bad code to get traceback exception

    def __init__(self, logfile=None, loglevels="", leveltext="",  loglevel="W", scrlevel="P"):
        self.logfile = logfile
        self.loglevels = loglevels
        self.leveltext = leveltext
        self.errorcount = 0
        self.warningcount = 0
        if not self.loglevels: self.loglevels = {'X': 0,       'S': 1,       'E': 2,       'P': 3,       'W': 4,       'I': 5,       'V': 6}
        if not self.leveltext: self.leveltext = ('Exception ', 'Severe:   ', 'Error:    ', 'Progress: ', 'Warning:  ', 'Info:     ', 'Verbose:  ')
        super(loggerobj, self).__setattr__("loglevel", "E") # Temp values so invalid log levels can be reported
        super(loggerobj, self).__setattr__("scrlevel", "E") #
        self.loglevel = loglevel
        self.scrlevel = scrlevel

    def __setattr__(self, name, value):
        if name in ("loglevel", "scrlevel"):
            if value in self.loglevels:
                (minlevel, minnum) = ("E",2) if name == "loglevel" else ("S", 1)
                if self.loglevels[value] < minnum:
                    value = minlevel
                    self.log(name + " increased to minimum level of " + minlevel, "E")
            else:
                self.log("Invalid " + name + " value: " + value, "S")
        super(loggerobj, self).__setattr__(name, value)
        if name == "scrlevel" : self._basescrlevel = value # Used by resetscrlevel

    def log(self, logmessage, msglevel="W"):
        levelval = self.loglevels[msglevel]
        message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + self.leveltext[levelval] + logmessage
        #message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:22] +" "+ self.leveltext[levelval] + logmessage  ## added milliseconds for timing tests
        if levelval <= self.loglevels[self.scrlevel]: print(message)
        if self.logfile and levelval <= self.loglevels[self.loglevel]: self.logfile.write(message + "\n")
        if msglevel == "S":
            print("\n **** Fatal error - exiting ****")
            sys.exit(1)
        if msglevel == "X": assert False, message
        if msglevel == "E": self.errorcount += 1
        if msglevel == "W": self.warningcount += 1

    def raisescrlevel(self, level): # Temproarily increase screen logging
        if level not in self.loglevels or level == "X" : self.log("Invalid scrlevel: " + level, "X")
        if self.loglevels[level] > self.loglevels[self.scrlevel]:
            current = self.scrlevel
            self.scrlevel = level
            self._basescrlevel = current
            self.log("scrlevel raised to " + level, "I")

    def resetscrlevel(self):
        self.scrlevel = self._basescrlevel


class parameters(object):
    # Object for holding parameters information, organised by class (eg logging)

    # Default parameters for use in pysilfont modules
    #   Names must be case-insensitively unique across all parameter classes
    #   Parameter types are deduced from the default values

    def __init__(self):
        # Default parameters for all modules
        defparams = {}
        defparams['system'] = {'version': silfont.__version__, 'copyright': silfont.__copyright__}  # Code treats these as read-only
        defparams['logging'] = {'scrlevel': 'P', 'loglevel': 'W'}
        defparams['backups'] = {'backup': True, 'backupdir': 'backups', 'backupkeep': 5}
        # Default parameters for UFO module
        defparams['outparams'] = OrderedDict([ # Use ordered dict so parameters show in logical order with -h p
            ("UFOversion", ""),  # UFOversion - defaults to existing unless a value is supplied
            ("indentIncr",       "  "),   # XML Indent increment
            ("indentFirst",      "  "),   # First XML indent
            ("indentML",         False),  # Should multi-line string values be indented?
            ("plistIndentFirst", ""),     # First indent amount for plists
            ('precision', 6),             # Decimal precision to use in XML output - both for real values and for attributes if float
            ("floatAttribs", ['xScale', 'xyScale', 'yxScale', 'yScale', 'angle']),  # Used with precision above
            ("intAttribs", ['pos', 'width', 'height', 'xOffset', 'yOffset', 'x', 'y']),
            ("sortDicts",        True),   # Should dict elements be sorted alphabetically?
            ("renameGlifs",      True),   # Rename glifs based on UFO3 suggested algorithm
            ("format1Glifs",     False),  # Force output format 1 glifs including UFO2-style anchors (for use with FontForge
            ("glifElemOrder",    ['advance', 'unicode', 'note',   'image',  'guideline', 'anchor', 'outline', 'lib']),  # Order to output glif elements
            ("attribOrders.glif",['pos', 'width', 'height', 'fileName', 'base', 'xScale', 'xyScale', 'yxScale', 'yScale', 'xOffset', 'yOffset',
                                  'x', 'y', 'angle', 'type', 'smooth', 'name', 'format', 'color', 'identifier'])
            ])
        defparams['ufometadata'] = {"checkfix": "check"}   # Apply metadata fixes when reading UFOs

        self.paramshelp = {} # Info used when outputting help about parame options
        self.paramshelp["classdesc"] = {
            "logging": "controls the level of log messages go to screen or log files.",
            "backups": "controls backup settings for scripts that output fonts - by default backups are made if the output font is overwriting the input font",
            "outparams": "Output options for UFOs - cover UFO version and normalization",
            "ufometadata": "controls if UFO metatdata be checked, or checked and fixed"
        }
        self.paramshelp["paramsdesc"] = {
            "scrlevel": "Logging level for screen messages - one of S,E,P.W,I or V",
            "loglevel": "Logging level for log file messages - one of E,P.W,I or V",
            "backup": "Should font backups be made",
            "backupdir": "Directory to use for font backups",
            "backupkeep": "How many backups to keep",
            "indentIncr": "XML Indent increment",
            "indentFirst": "First XML indent",
            "indentML": "Should multi-line string values be indented?",
            "plistIndentFirst": "First indent amount for plists",
            "sortDicts": "Should dict elements be sorted alphabetically?",
            "precision": "Decimal precision to use in XML output - both for real values and for attributes if numeric",
            "renameGlifs": "Rename glifs based on UFO3 suggested algorithm",
            "UFOversion": "UFOversion to output - defaults to version of the input UFO",
            "format1Glifs": "Force output format 1 glifs including UFO2-style anchors (was used with FontForge; no longer needed)",
            "glifElemOrder": "Order to output glif elements",
            "floatAttribs": "List of float attributes - used when setting decimal precision",
            "intAttribs": "List of attributes that should be integers",
            "attribOrders.glif": "Order in which to output glif attributes",
            "checkfix": "Should check & fix tests be done - one of None, Check or Fix"
        }
        self.paramshelp["defaultsdesc"] = { # For use where default needs clarifying with text
            "indentIncr" : "<two spaces>",
            "indentFirst": "<two spaces>",
            "plistIndentFirst": "<No indent>",
            "UFOversion": "<Existing version>"
        }

        self.classes = {}  # Dictionary containing a list of parameters in each class
        self.paramclass = {}  # Dictionary of class name for each parameter name
        self.types = {}  # Python type for each parameter deduced from initial values supplied
        self.listtypes = {}  # If type is dict, the type of values in the dict
        self.logger = loggerobj()
        defset = _paramset(self, "default", "defaults")
        self.sets = {"default": defset}
        self.lcase = {}  # Lower case index of parameters names
        for classn in defparams:
            self.classes[classn] = []
            for parn in defparams[classn]:
                value = defparams[classn][parn]
                self.classes[classn].append(parn)
                self.paramclass[parn] = classn
                self.types[parn] = type(value)
                if type(value) is list: self.listtypes[parn] = type(value[0])
                super(_paramset, defset).__setitem__(parn, value)  # __setitem__ in paramset does not allow new values!
                self.lcase[parn.lower()] = parn

    def addset(self, name, sourcedesc=None, inputdict=None, configfile=None, copyset=None):
        # Create a subset from one of a dict, config file or existing set
        # Only one option should used per call
        # sourcedesc should be added for user-supplied data (eg config file) for reporting purposes
        dict = {}
        if configfile:
            config = configparser.ConfigParser()
            config.readfp(io.open(configfile, encoding="utf-8"))
            if sourcedesc is None: sourcedesc = configfile
            for classn in config.sections():
                for item in config.items(classn):
                    parn = item[0]
                    if self.paramclass[parn] == "system":
                        self.logger.log("Can't change " + parn + " parameter via config file", "S")
                    val = item[1].strip('"').strip("'")
                    dict[parn] = val
        elif copyset:
            if sourcedesc is None: sourcedesc = "Copy of " + copyset
            for parn in self.sets[copyset]:
                dict[parn] = self.sets[copyset][parn]
        elif inputdict:
            dict = inputdict
        if sourcedesc is None: sourcedesc = "unspecified source"
        self.sets[name] = _paramset(self, name, sourcedesc, dict)

    def printhelp(self):
        phelp = self.paramshelp
        print("\nMost pysilfont scripts have -p, --params options which can be used to change default behaviour of scripts.  For example '-p scrlevel=w' will log warning messages to screen \n")
        print("Listed below are all such parameters, grouped by purpose.  Not all apply to all scripts - "
              "in partucular outparams and ufometadata only apply to scripts using pysilfont's own UFO code")
        for classn in ("logging", "backups", "ufometadata", "outparams"):
            print("\n" + classn[0].upper() + classn[1:] + " - " + phelp["classdesc"][classn])
            for param in self.classes[classn]:
                if param == "format1Glifs": continue # Param due to be phased out
                paramdesc = phelp["paramsdesc"][param]
                paramtype = self.types[param].__name__
                defaultdesc = phelp["defaultsdesc"][param] if param in phelp["defaultsdesc"] else self.sets["default"][param]
                print('    {:<20}: {}'.format(param, paramdesc))
                print('       (Type: {:<6} Default: {})'.format(paramtype + ",", defaultdesc))
        print("\nNote parameter names are case-insensitive\n")
        print("For more help see https://github.com/silnrsi/pysilfont/blob/master/docs/parameters.md\n")

class _paramset(dict):
    # Set of parameter values
    def __init__(self, params, name, sourcedesc, inputdict=None):
        if inputdict is None: inputdict = {}
        self.name = name
        self.sourcedesc = sourcedesc  # Description of source for reporting
        self.params = params  # Parent parameters object
        for parn in inputdict:
            if params.paramclass[parn] == "system": # system values can't be changed
                if inputdict[parn] != params.sets["default"][parn]:
                    self.params.logger.log("Can't change " + parn + " - system parameters can't be changed", "X")
                else:
                    super(_paramset, self).__setitem__(parn, inputdict[parn])
            else:
                self[parn] = inputdict[parn]

    def __setitem__(self, parn, value):
        origvalue = value
        origparn = parn
        parn = parn.lower()
        if self.params.paramclass[origparn] == "system":
            self.params.logger.log("Can't change " + parn + " - system parameters are read-only", "X")
        if parn not in self.params.lcase:
            self.params.logger.log("Invalid parameter " + origparn + " from " + self.sourcedesc, "S")
        else:
            parn = self.params.lcase[parn]
        ptyp = self.params.types[parn]
        if ptyp is bool:
            value = str2bool(value)
            if value is None: self.params.logger.log(self.sourcedesc+" parameter "+origparn+" must be boolean: " + origvalue, "S")
        if ptyp is list:
            if type(value) is not list: value = value.split(",")  # Convert csv string into list
            if len(value) < 2: self.params.logger.log(self.sourcedesc+" parameter "+origparn+" must have a list of values: " + origvalue, "S")
            valuesOK = True
            listtype = self.params.listtypes[parn]
            for i, val in enumerate(value):
                if listtype is bool:
                    val = str2bool(val)
                    if val is None: self.params.logger.log (self.sourcedesc+" parameter "+origparn+" must contain boolean values: " + origvalue, "S")
                    value[i] = val
                if type(val) != listtype: valuesOK = False
            if not valuesOK: self.params.logger.log("Invalid "+paramsource+" parameter type for "+origparn+": "+self.params.types[parn], "S")
        if parn in ("loglevel", "scrlevel"):  # Need to check log level is valid before setting it since otherwise logging will fail
            value = value.upper()
            if value not in self.params.logger.loglevels: self.params.logger.log (self.sourcedesc+" parameter "+parn+" invalid", "S")
        super(_paramset, self).__setitem__(parn, value)

    def updatewith(self, update, sourcedesc=None, log=True):
        # Update a set with values from another set
        if sourcedesc is None: sourcedesc = self.params.sets[update].sourcedesc
        for parn in self.params.sets[update]:
            oldval = self[parn] if parn in self else ""
            self[parn] = self.params.sets[update][parn]
            if log and oldval != "" and self[parn] != oldval:
                old = str(oldval)
                new = str(self[parn])
                if old != old.strip() or new != new.strip():   # Add quotes if there are leading or trailing spaces
                    old = '"'+old+'"'
                    new = '"'+new+'"'
                self.params.logger.log(sourcedesc + " parameters: changing "+parn+" from " + old + " to " + new, "I")


class csvreader(object):    # Iterator for csv files, skipping comments and checking number of fields
    def __init__(self, filename, minfields=0, maxfields=999, numfields=None, logger=None):
        self.filename = filename
        self.minfields = minfields
        self.maxfields = maxfields
        self.numfields = numfields
        self.logger = logger if logger else loggerobj()   # If no logger supplied, will just log to screen
        # Open the file and create reader
        try:
            file = io.open(filename, "rt", encoding="utf-8")
        except Exception as e:
            print(e)
            sys.exit(1)
        self.reader = csv.reader(file)
        # Read first line then reset; this is so scripts can analyse first line before starting iterating
        self.firstline = next(self.reader, None)
        file.seek(0)

    def __setattr__(self, name, value):
        if name == "numfields" and value is not None:  # If numfields is changed, reset min and max fields
            self.minfields = value
            self.maxfields = value
        super(csvreader, self).__setattr__(name, value)

    def __iter__(self):
        for row in self.reader:
            self.line_num = self.reader.line_num-1 # Count is out by 1 due to reading first lin in __init__
            if row == []: continue  # Skip blank lines
            if row[0].lstrip().startswith("#"): continue  # Skip comments - ie lines starting with  #
            if len(row) < self.minfields or len(row) > self.maxfields:
                self.logger.log("Invalid number of fields on line " + str(self.line_num) + " in "+self.filename, "E" )
                continue
            yield row


def execute(tool, fn, scriptargspec, chain = None):
    # Function to handle parameter parsing, font and file opening etc in command-line scripts
    # Supports opening (and saving) fonts using PysilFont UFO (UFO), fontParts (FP) or fontTools (FT)
    # Special handling for:
    #   -d  variation on -h to print extra info about defaults
    #   -q  quiet mode - only output a single line with count of errors (if there are any)
    #   -l  opens log file and also creates a logger function to write to the log file
    #   -p  other parameters. Includes backup settings and loglevel/scrlevel settings for logger
    #       for UFOlib scripts, also includes all outparams keys and ufometadata settings

    argspec = list(scriptargspec)

    chainfirst = False
    if chain == "first": # If first call to execute has this set, only do the final return part of chaining
        chainfirst = True
        chain = None

    params = chain["params"] if chain else parameters()
    logger = chain["logger"] if chain else params.logger  # paramset has already created a basic logger
    argv   = chain["argv"]   if chain else sys.argv

    if tool == "UFO":
        from silfont.ufo import Ufont
    elif tool == "FT":
        from fontTools import ttLib
    elif tool == "FP":
        from fontParts.world import OpenFont
    elif tool == "" or tool is None:
        tool = None
    else:
        logger.log("Invalid tool in call to execute()", "X")
        return
    basemodule = sys.modules[fn.__module__]
    poptions = {}
    poptions['prog'] = splitfn(argv[0])[1]
    poptions['description'] = basemodule.__doc__
    poptions['formatter_class'] = argparse.RawDescriptionHelpFormatter
    epilog = "For more help options use -h ?.  For more documentation see https://github.com/silnrsi/pysilfont/blob/master/docs/scripts.md#" + poptions['prog'] + "\n\n"
    poptions['epilog'] = epilog + "Version: " + params.sets['default']['version'] + "\n" + params.sets['default']['copyright']

    parser = argparse.ArgumentParser(**poptions)
    parser._optionals.title = "other arguments"


    # Add standard arguments
    standardargs = {
            'quiet': ('-q', '--quiet', {'help': 'Quiet mode - only display severe errors', 'action': 'store_true'}, {}),
            'log': ('-l', '--log', {'help': 'Log file'}, {'type': 'outfile'}),
            'params': ('-p', '--params', {'help': 'Other parameters - see parameters.md for details', 'action': 'append'}, {'type': 'optiondict'}),
            'nq': ('--nq', {'help': argparse.SUPPRESS, 'action': 'store_true'}, {})}

    suppliedargs = []
    for a in argspec:
        argn = a[:-2][-1]  # [:-2] will give either 1 or 2, the last of which is the full argument name
        if argn[0:2] == "--": argn = argn[2:]  # Will start with -- for options
        suppliedargs.append(argn)
    for arg in sorted(standardargs):
        if arg not in suppliedargs: argspec.append(standardargs[arg])

    defhelp = False
    if "-h" in argv: # Look for help option supplied
        pos = argv.index("-h")
        if pos < len(argv)-1: # There is something following -h!
            opt = argv[pos+1]
            if opt in ("d", "defaults"):
                defhelp = True # Normal help will be displayed with default info displayed by the epilog
                deffiles = []
                defother = []
            elif opt in ("p", "params"):
                params.printhelp()
                sys.exit(0)
            else:
                if opt != "?":
                    print("Invalid -h value")
                    print("-h ? displays help options")
                print("-h d (or -h defaults) lists details of default values for arguments and parameters")
                print("-h p (or -h params) gives help on parameters that can be set with -p or --params")
                sys.exit(0)

    quiet = True if "-q" in argv and '--nq' not in argv else False
    if quiet: logger.scrlevel = "S"

    # Process the supplied argument specs, add args to parser, store other info in arginfo
    arginfo = []
    logdef = None
    for a in argspec:
        # Process all but last tuple entry as argparse arguments
        nonkwds = a[:-2]
        kwds = a[-2]
        parser.add_argument(*nonkwds, **kwds)
        # Create ainfo, a dict of framework keywords using argument name
        argn = nonkwds[-1]  # Find the argument name from first 1 or 2 tuple entries
        if argn[0:2] == "--": argn = argn[2:]  # Will start with -- for options
        ainfo=dict(a[-1]) #Make a copy so original argspec is not changed
        for key in ainfo: # Check all keys are valid
            if key not in ("def", "type", "optlog") : logger.log("Invalid argspec framework key: " + key, "X")
        ainfo['name']=argn
        if argn == 'log':
            logdef = ainfo['def'] if 'def' in ainfo else None
            optlog = ainfo['optlog'] if 'optlog' in ainfo else False
        arginfo.append(ainfo)
        if defhelp:
            arg = nonkwds[0]
            if 'def' in ainfo:
                defval = ainfo['def']
                if argn == 'log' and logdef: defval += " in logs subdirectory"
                deffiles.append([arg, defval])
            elif 'default' in kwds:
                defother.append([arg, kwds['default']])

    # if -h d specified, change the help epilog to info about argument defaults
    if defhelp:
        if not (deffiles or defother):
            deftext = "No defaults for parameters/options"
        else:
            deftext = "Defaults for parameters/options - see user docs for details\n"
        if deffiles:
            deftext = deftext + "\n  Font/file names\n"
            for (param, defv) in deffiles:
                deftext = deftext + '    {:<20}{}\n'.format(param, defv)
        if defother:
            deftext = deftext + "\n  Other parameters\n"
            for (param, defv) in defother:
                deftext = deftext + '    {:<20}{}\n'.format(param, defv)
        parser.epilog = deftext + "\n\n" + parser.epilog

    # Parse the command-line arguments. If errors or -h used, procedure will exit here
    args = parser.parse_args(argv[1:])

    # Process the first positional parameter to get defaults for file names
    fppval = getattr(args, arginfo[0]['name'])
    if isinstance(fppval, list): # When nargs="+" or nargs="*" is used a list is returned
        (fppath, fpbase, fpext) = splitfn(fppval[0])
        if len(fppval) > 1 : fpbase = "wildcard"
    else:
        if fppval is None: fppval = ""  # For scripts that can be run with no positional parameters
        (fppath, fpbase, fpext) = splitfn(fppval)  # First pos param use for defaulting

    # Process parameters
    if chain:
        execparams = params.sets["main"]
        args.params = {}  # clparams not used when chaining
    else:
        # Read config file from disk if it exists
        configname = os.path.join(fppath, "pysilfont.cfg")
        if os.path.exists(configname):
            params.addset("config file", configname, configfile=configname)
        else:
            params.addset("config file")  # Create empty set
        if not quiet and "scrlevel" in params.sets["config file"]: logger.scrlevel = params.sets["config file"]["scrlevel"]

        # Process command-line parameters
        clparams = {}
        if 'params' in args.__dict__:
            if args.params is not None:
                for param in args.params:
                    x = param.split("=", 1)
                    if len(x) != 2:
                        logger.log("params must be of the form 'param=value'", "S")
                    if x[1] == "\\t": x[1] = "\t"  # Special handling for tab characters
                    clparams[x[0]] = x[1]

        args.params = clparams
        params.addset("command line", "command line", inputdict=clparams)
        if not quiet and "scrlevel" in params.sets["command line"]: logger.scrlevel = params.sets["command line"]["scrlevel"]

        # Create main set of parameters based on defaults then update with config file values and command line values
        params.addset("main", copyset="default")
        params.sets["main"].updatewith("config file")
        params.sets["main"].updatewith("command line")
        execparams = params.sets["main"]

    # Set up logging
    if chain:
        setattr(args, 'logger', logger)
        args.logfile = logger.logfile
    else:
        logfile = None
        logname = args.log if 'log' in args.__dict__ and args.log is not None else ""
        if 'log' in args.__dict__:
            if logdef is not None and (logname != "" or optlog == False):
                (path, base, ext) = splitfn(logname)
                (dpath, dbase, dext) = splitfn(logdef)
                if not path:
                    if base and ext:  # If both specified then use cwd, ie no path
                        path = ""
                    else:
                        path = (fppath if dpath == "" else os.path.join(fppath, dpath))
                        path = os.path.join(path, "logs")
                if not base:
                    if dbase == "":
                        base = fpbase
                    elif dbase[0] == "_":  # Append to font name if starts with _
                        base = fpbase + dbase
                    else:
                        base = dbase
                if not ext and dext: ext = dext
                logname = os.path.join(path, base+ext)
            if logname == "":
                logfile = None
            else:
                (logname, logpath, exists) = fullpath(logname)
                if not exists:
                    (parent,subd) = os.path.split(logpath)
                    if subd == "logs" and os.path.isdir(parent): # Create directory if just logs subdir missing
                        logger.log("Creating logs subdirectory in " + parent, "P")
                        os.mkdir(logpath)
                    else: # Fails, since missing dir is probably a typo!
                        logger.log("Directory " + parent + " does not exist", "S")
                logger.log('Opening log file for output: ' + logname, "P")
                try:
                    logfile = io.open(logname, "w", encoding="utf-8")
                except Exception as e:
                    print(e)
                    sys.exit(1)
                args.log = logfile
        # Set up logger details
        logger.loglevel = execparams['loglevel'].upper()
        logger.logfile = logfile
        if not quiet: logger.scrlevel = "E"  # suppress next log message from screen
        logger.log("Running:  " + " ".join(argv), "P")
        if not quiet: logger.scrlevel = execparams['scrlevel'].upper()
        setattr(args, 'logger', logger)

# Process the argument values returned from argparse

    outfont = None
    infontlist = []
    for c, ainfo in enumerate(arginfo):
        aval = getattr(args, ainfo['name'])
        if ainfo['name'] in ('params', 'log'): continue  # params and log already processed
        atype = None
        adef = None
        if 'type' in ainfo:
            atype = ainfo['type']
            if atype not in ('infont', 'outfont', 'infile', 'outfile', 'incsv', 'filename', 'optiondict'):
                logger.log("Invalid type of " + atype + " supplied in argspec", "X")
            if atype != 'optiondict':  # All other types are file types, so adef must be set, even if just to ""
                adef = ainfo['def'] if 'def' in ainfo else ""
            if adef is None and aval is None:  # If def explicitly set to None then this is optional
                setattr(args, ainfo['name'], None)
                continue

        if c == 0:
            if aval is None : logger.log("Invalid first positional parameter spec", "X")
            if aval[-1] in ("\\","/"): aval = aval[0:-1]  # Remove trailing slashes
        else:  #Handle defaults for all but first positional parameter
            if adef is not None:
                if not aval: aval = ""
                if aval == "" and adef == "":  # Only valid for output font parameter
                    if atype != "outfont":
                        logger.log("No value suppiled for " + ainfo['name'], "S")
                        ## Not sure why this needs to fail - we need to cope with other optional file or filename parameters
                (apath, abase, aext) = splitfn(aval)
                (dpath, dbase, dext) = splitfn(adef)  # dpath should be None
                if not apath:
                    if abase and aext:  # If both specified then use cwd, ie no path
                        apath = ""
                    else:
                        apath = fppath
                if not abase:
                    if dbase == "":
                        abase = fpbase
                    elif dbase[0] == "_":  # Append to font name if starts with _
                        abase = fpbase + dbase
                    else:
                        abase = dbase
                if not aext:
                    if dext:
                        aext = dext
                    elif (atype == 'outfont' or atype == 'infont'): aext = fpext
                aval = os.path.join(apath, abase+aext)

        # Open files/fonts
        if atype == 'infont':
            if tool is None:
                logger.log("Can't specify a font without a font tool", "X")
            infontlist.append((ainfo['name'], aval))  # Build list of fonts to open when other args processed
        elif atype == 'infile':
            logger.log('Opening file for input: '+aval, "P")
            try:
                aval = io.open(aval, "r", encoding="utf-8")
            except Exception as e:
                print(e)
                sys.exit(1)
        elif atype == 'incsv':
            logger.log('Opening file for input: '+aval, "P")
            aval = csvreader(aval, logger=logger)
        elif atype == 'outfile':
            (aval, path, exists) = fullpath(aval)
            if not exists:
                logger.log("Output file directory " + path + " does not exist", "S")
            logger.log('Opening file for output: ' + aval, "P")
            try:
                aval = io.open(aval, 'w', encoding="utf-8")
            except Exception as e:
                print(e)
                sys.exit(1)
        elif atype == 'outfont':
            if tool is None:
                logger.log("Can't specify a font without a font tool", "X")
            outfont = aval
            outfontpath = apath
            outfontbase = abase
            outfontext = aext

        elif atype == 'optiondict':  # Turn multiple options in the form ['opt1=a', 'opt2=b'] into a dictionary
            avaldict={}
            if aval is not None:
                for option in aval:
                    x = option.split("=", 1)
                    if len(x) != 2:
                        logger.log("options must be of the form 'param=value'", "S")
                    if x[1] == "\\t": x[1] = "\t"  # Special handling for tab characters
                    avaldict[x[0]] = x[1]
            aval = avaldict

        setattr(args, ainfo['name'], aval)

# Open fonts - needs to be done after processing other arguments so logger and params are defined

    for name, aval in infontlist:
        if chain and name == 'ifont':
            aval = chain["font"]
        else:
            if tool == "UFO": aval = Ufont(aval, params=params)
            if tool == "FT" : aval = ttLib.TTFont(aval)
            if tool == "FP" : aval = OpenFont(aval)
        setattr(args, name, aval)  # Assign the font object to args attribute

# All arguments processed, now call the main function
    setattr(args, "paramsobj", params)
    setattr(args, "cmdlineargs", argv)
    newfont = fn(args)
# If an output font is expected and one is returned, output the font
    if chainfirst: chain = True # Special handling for first call of chaining
    if newfont:
        if chain:  # return font to be handled by chain()
            return (args, newfont)
        else:
            if outfont:
                # Backup the font if output is overwriting original input font
                if outfont == infontlist[0][1]:
                    backupdir = os.path.join(outfontpath, execparams['backupdir'])
                    backupmax = int(execparams['backupkeep'])
                    backup = str2bool(execparams['backup'])

                    if backup:
                        if not os.path.isdir(backupdir):  # Create backup directory if not present
                            try:
                                os.mkdir(backupdir)
                            except Exception as e:
                                print(e)
                                sys.exit(1)
                        backupbase = os.path.join(backupdir, outfontbase+outfontext)
                        # Work out backup name based on existing backups
                        nums = sorted([int(i[len(backupbase)+1-len(i):-1]) for i in glob(backupbase+".*~")])  # Extract list of backup numbers from existing backups
                        newnum = max(nums)+1 if nums else 1
                        backupname = backupbase+"."+str(newnum)+"~"
                        # Backup the font
                        logger.log("Backing up input font to "+backupname, "P")
                        shutil.copytree(outfont, backupname)
                        # Purge old backups
                        for i in range(0, len(nums) - backupmax + 1):
                            backupname = backupbase+"."+str(nums[i])+"~"
                            logger.log("Purging old backup "+backupname, "I")
                            shutil.rmtree(backupname)
                    else:
                        logger.log("No font backup done due to backup parameter setting", "W")
                # Output the font
                if tool in ("FT", "FP"):
                    logger.log("Saving font to " + outfont, "P")
                    newfont.save(outfont)
                else:  # Must be Pyslifont Ufont
                    newfont.write(outfont)
            else:
                logger.log("Font returned to execute() but no output font is specified in arg spec", "X")
    elif chain:             # ) When chaining return just args - the font can be accessed by args.ifont
        return (args, None) # ) assuming that the script has not changed the input font

    if logger.errorcount or logger.warningcount:
        message = "Command completed with " + str(logger.errorcount) + " errors and " + str(logger.warningcount) + " warnings"
        if logger.scrlevel in ("S", "E") and logname != "":
            if logger.scrlevel == "S" or logger.warningcount: message = message + " - see " + logname
        if logger.errorcount:
            if quiet: logger.raisescrlevel("E")
            logger.log(message, "E")
            logger.resetscrlevel()
        else:
            logger.log(message, "P")
        if logger.scrlevel == "P" and logger.warningcount: logger.log("See log file for warning messages or rerun with '-p scrlevel=w'", "P")
    else:
        logger.log("Command completed with no warnings", "P")

    return (args, newfont)


def chain(argv, function, argspec, font, params, logger, quiet):  # Chain multple command-line scripts using UFO module together without writing font to disk
    ''' argv is a command-line call to a script in sys.argv format.  function and argspec are from the script being called.
    Although input font name must be supplied for the command line to be parsed correctly by execute() it is not used - instead the supplied
    font object is used. Similarly -params, logfile and quiet settings in argv are not used by execute() when chaining is used'''
    if quiet and "-q" not in argv: argv.append("-q")
    logger.log("Chaining to " + argv[0], "P")
    font = execute("UFO", function, argspec, 
        {'argv' : argv, 
            'font'  : font,
            'params': params,
            'logger': logger,
            'quiet' : quiet})
    logger.log("Returning from " + argv[0], "P")
    return font


def splitfn(fn):  # Split filename into path, base and extension
    if fn:  # Remove trailing slashes
        if fn[-1] in ("\\","/"): fn = fn[0:-1]
    (path, base) = os.path.split(fn)
    (base, ext) = os.path.splitext(base)
    # Handle special case where just a directory is supplied
    if ext == "":  # If there's an extension, treat as file name, eg a ufo directory
        if os.path.isdir(fn):
            path = fn
            base = ""
    return (path, base, ext)


def str2bool(v):  # If v is not a boolean, convert from string to boolean
    if type(v) == bool: return v
    v = v.lower()
    if v in ("yes", "y", "true", "t", "1"):
        v = True
    elif v in ("no", "n", "false", "f", "0"):
        v = False
    else:
        v = None
    return v

def fullpath(filen): # Changes file name to one with full path and checks directory exists
    fullname = os.path.abspath(filen)
    (fpath,dummy) = os.path.split(fullname)
    return fullname, fpath, os.path.isdir(fpath)
