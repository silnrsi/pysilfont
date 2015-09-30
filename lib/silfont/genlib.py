#!/usr/bin/env python
'General classes and functions for use in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '1.0.0'

from xml.etree import cElementTree as ET
import re, sys, os, codecs, argparse, datetime

_elementprotect = {
    '&' : '&amp;',
    '<' : '&lt;',
    '>' : '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;'

class ETWriter(object) :
    """ General purpose ElementTree pretty printer complete with options for attribute order
        beyond simple sorting, and which elements should use cdata """

    def __init__(self, etree, namespaces = None, attributeOrder = {}, takesCData = set(), indentIncr = "  ", indentFirst = "  ", indentML = False):
        self.root = etree
        if namespaces is None : namespaces = {}
        self.namespaces = namespaces
        self.attributeOrder = attributeOrder    # Sort order for attributes - just one list for all elements
        self.takesCData = takesCData
        self.indentIncr = indentIncr            # Incremental increase in indent
        self.indentFirst = indentFirst          # Indent for first level
        self.indentML = indentML                # Add indent to multi-line strings

    def _protect(self, txt, base=_attribprotect) :
        return re.sub(ur'['+ur"".join(base.keys())+ur"]", lambda m: base[m.group(0)], txt)

    def serialize_xml(self, write, base = None, indent = '') :
        """Output the object using write() in a normalised way:
                If namespaces are used, use serialize_nsxml instead"""
        outstr=""

        if base is None :
            base = self.root
            outstr += '<?xml version="1.0" encoding="UTF-8"?>\n'
            if '.doctype' in base.attrib : outstr += u'<!DOCTYPE {}>\n'.format(base.attrib['.doctype'])

        tag = base.tag
        attribs = base.attrib

        if '.comments' in attribs :
            for c in attribs['.comments'].split(",") : outstr += u'{}<!--{}-->\n'.format(indent, c)

        outstr += u'{}<{}'.format(indent, tag)

        for k in sorted(attribs.keys(), cmp=lambda x,y: cmp(self.attributeOrder.get(x, 999), self.attributeOrder.get(y, 999)) or cmp(x, y)) :
            if k[0] <> '.' : outstr += u' {}="{}"'.format(k, attribs[k])
        if base :
            outstr += '>\n'
            if base == self.root:
                incr = self.indentFirst
            else:
                incr = self.indentIncr
            write(outstr); outstr=""
            for b in base : self.serialize_xml(write, base=b, indent=indent + incr)
            outstr += '{}</{}>\n'.format(indent, tag)
        elif base.text and base.text.strip() :
            if tag not in self.takesCData :
                t = base.text
                if self.indentML : t = t.replace('\n', '\n' + indent)
                t = self._protect(t, base=_elementprotect)
            else :
                t = "<![CDATA[\n\t" + indent + base.text.replace('\n', '\n\t' + indent) + "\n" + indent + "]]>"
            outstr += u'>{}</{}>\n'.format(t, tag)
        else :
            outstr += '/>\n'

        if '.commentsafter' in base.attrib :
            for c in base.attrib['.commentsafter'].split(",") : outstr += u'{}<!--{}-->\n'.format(indent, c)

        write(outstr)

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

    def _nsprotectattribs(self, attribs, localattribs, namespaces) :
        if attribs is not None :
            for k, v in attribs.items() :
                (lt, lq, lns) = self._localisens(k)
                if lns and lns not in namespaces :
                    namespaces[lns] = lq
                    localattribs['xmlns:'+lq] = lns
                localattribs[lt] = v

    def serialize_nsxml(self, write, base = None, indent = '', topns = True, namespaces = {}) :
        """Output the object using write() in a normalised way:
                topns if set puts all namespaces in root element else put them as low as possible"""
        ## Needs amending to mirror changes in serialize_xml for dummy attributes (and efficiency)"""
        if base is None :
            base = self.root
            write('<?xml version="1.0" encoding="UTF-8"?>\n')
            doctype = base.attrib['_doctype'] if '_doctype' in base.attrib else None
            if doctype is not None:
                del base.attrib["_doctype"]
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

        if '_comments' in base.attrib :
            for c in base.attrib['_comments'].split(",") :
               write(u'{}<!--{}-->\n'.format(indent, c))
            del base.attrib["_comments"]

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
                if base == self.root:
                    incr = self.indentFirst
                else:
                    incr = self.indentIncr
                self.serialize_nsxml(write, base=b, indent=indent + incr, topns=topns, namespaces=namespaces.copy())
            write('{}</{}>\n'.format(indent, tag))
        elif base.text :
            if base.text.strip() :
                if tag not in self.takesCData :
                    t = base.text

                    if self.indentML : t = t.replace('\n', '\n' + indent)
                    t = self._protect(t, base=_elementprotect)
                else :
                    t = "<![CDATA[\n\t" + indent + base.text.replace('\n', '\n\t' + indent) + "\n" + indent + "]]>"
                write(u'>{}</{}>\n'.format(t, tag))
            else :
                write('/>\n')
        else :
            write('/>\n')

        if '_commentsafter' in base.attrib :
            for c in base.attrib['_commentsafter'].split(",") :
               write(u'{}<!--{}-->\n'.format(indent, c))
            del base.attrib["_commentsafter"]

    def add_namespace(self, q, ns) :
        if ns in self.namespaces : return self.namespaces[ns]
        self.namespaces[ns] = q
        return q

class dirTree(dict) :
    """ An object to hold list of all files and directories in a directory
        with option to read sub-directory contents into dirTree objects.
        Iterates through readSub levels of subfolders """
    def __init__(self,dirn,readSub = 9999) :
        self.removedfiles = {} # List of files that have been renamed or deleted since reading from disk
        for name in os.listdir(dirn) :
            if name[-1:] == "~" : continue
            item=dirTreeItem()
            if os.path.isdir(os.path.join(dirn, name)) :
                item.type = "d"
                if readSub :
                    item.dirtree = dirTree(os.path.join(dirn,name),readSub-1)
            self[name] = item

    def subTree(self,path) : # Returns dirTree object for a subtree based on subfolder name(s)
        # 'path' can be supplied as either a relative path (eg "subf/subsubf") or array (eg ['subf','subsubf']
        if type(path) is str : path = self._split(path)
        subf=path[0]
        if subf in self:
            dtree =  self[subf].dirtree
        else : return None

        if len(path) == 1 :
            return dtree
        else :
            path.pop(0)
            return dtree.subTree(path)

    def _split(self,path) : # Turn a relative path into an array of subfolders
        npath = [os.path.split(path)[1]]
        while os.path.split(path)[0] :
            path = os.path.split(path)[0]
            npath.insert(0,os.path.split(path)[1])
        return npath

class dirTreeItem(object) :

    def __init__(self, type = "f", dirtree = None, read = False, added = False, changed = False, towrite = False, written = False, fileObject = None, fileType = None, flags = {}) :
        self.type = type                # "d" or "f"
        self.dirtree = dirtree          # dirtree for a sub-directory
        # Remaining properties are for calling scripts to use as they choose to track actions etc
        self.read = read                # Item has been read by the script
        self.added = added              # Item has been added to dirtree, so does not exist on disk
        self.changed = changed          # Item has been changed, so may need updating on disk
        self.towrite = towrite          # Item should be written out to disk
        self.written = written          # Item has been written to disk
        self.fileObject = fileObject    # An object representing the file
        self.fileType = fileType        # The type of the file object
        self.flags = {}                 # Any other flags a script might need

    def setinfo(self, read = None, added = None, changed = None, towrite = None, written = None, fileObject = None, fileType = None, flags = None) :
        pass
        if read : self.read = read
        if added : self.added = added
        if changed : self.changed = changed
        if towrite: self.towrite = towrite
        if written : self.written = written
        if fileObject is not None : self.fileObject = fileObject
        if fileType : self.fileType = fileType
        if flags : self.flags = flags

class xmlitem(object) :
    """ The xml data item for an xml file"""

    def __init__(self, dirn = None, filen = None, parse = True ) :
        self._contents = {}
        self.dirn = dirn
        self.filen = filen
        self.inxmlstr = ""
        self.outxmlstr = ""
        self.etree = None
        self.type = None
        if filen and dirn :
            try :
                inxml=open(os.path.join( dirn, filen), "r")
            except Exception as e :
                print e
                sys.exit(1)
            for line in inxml.readlines() :
                self.inxmlstr = self.inxmlstr + line
            inxml.close()
            if parse :
                self.etree = ET.fromstring(self.inxmlstr)

    def write_to_xml(self,text) : # Used by ETWriter.serialize_xml()
        self.outxmlstr = self.outxmlstr + text

    def write_to_file(self,dirn,filen) :
        outfile=codecs.open(os.path.join(dirn,filen),'w','utf-8')
        outfile.write(self.outxmlstr)
        outfile.close

    # Define methods so it acts like an imumtable container -
    # changes should be made via object methods
    def __len__(self):
        return len(self._contents)
    def __getitem__(self, key):
        return self._contents[key]
    def __iter__(self):
        return iter(self._contents)
    def keys(self) :
        return self._contents.keys()

class loggerobj(object) :
    # For handling log messages.
    # Use S for severe errors caused by data, parameters supplied by user etc
    # Use X for severe errors caused by bad code to get traceback exception

    def __init__(self, logfile = None, loglevels = "", leveltext = "",  loglevel = "W", scrlevel = "P") :
        self.logfile = logfile
        self.loglevels = loglevels
        self.leveltext = leveltext
        if not self.loglevels : self.loglevels = { 'X': 0,       'S':1,        'E':2,        'P':3,        'W':4,        'I':5,        'V':6}
        if not self.leveltext : self.leveltext = ( 'Exception ', 'Severe:   ', 'Error:    ', 'Progress: ', 'Warning:  ', 'Info:     ', 'Verbose:  ')
        self.loglevel = "2"; self.scrlevel = "2" # Temp values so invalid log levels can be reported
        if loglevel in self.loglevels :
            self.loglevel = self.loglevels[loglevel]
        else:
            self.log("Invalid loglevel value", "S")
        if scrlevel in self.loglevels :
            self.scrlevel = self.loglevels[scrlevel]
        else:
            self.log("Invalid scrlevel value", "S")

    def log(self, logmessage, msglevel = "I") :
        levelval = self.loglevels[msglevel]
        message = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S ") + self.leveltext[levelval] + logmessage
        #message = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f ") + self.leveltext[levelval] + logmessage ## added milliseconds for timing tests
        if levelval <= self.scrlevel : print message
        if self.logfile and levelval <= self.loglevel : self.logfile.write(message + "\n")
        if msglevel == "S" :
            print "\n **** Fatal error - exiting ****"
            sys.exit(1)
        if msglevel == "X" :assert False, message

def makeAttribOrder(attriblist) : # Turn a list of attrib names into an attributeOrder dict for ETWriter
        return dict(map(lambda x:(x[1], x[0]), enumerate(attriblist)))


def execute(tool, fn, argspec) :
    # Function to handle parameter parsing, font and file opening etc in command-line scripts
    # Supports opening (and saving) fonts using FontForge (FF) or PysilFont UFOlib (PSFU)
    # Special handling for:
    #   -d        variation on -h to print extra info about defaults
    #   -q  quiet mode - suppresses progress messages and sets screen logging to errors only
    #   -l  opens log file and also creates a logger function to write to the log file
    #   -p  includes loglevel and scrlevel settings for logger
    #       for UFOlib scripts, also includes all font.outparams keys except for attribOrder
    #   -v  for UFOlib scripts this sets font.outparams(UFOversion)

    ff = False
    psfu = False
    if tool == "FF" :
        ff=True
        import fontforge
        if fontforge.hasUserInterface() :
            return # Execute is for command-line use
    elif tool == "PSFU" :
        psfu = True
        from UFOlib import Ufont
    elif tool == "" or tool is None :
        tool = None
    else :
        print "Invalid tool in call to execute()"
        return

    basemodule = sys.modules[fn.__module__]
    poptions = {}
    poptions['prog'] = _splitfn(sys.argv[0])[1]
    poptions['description'] = basemodule.__doc__
    poptions['formatter_class'] = argparse.RawDescriptionHelpFormatter
    if hasattr(basemodule, '__version__') : poptions['epilog'] = "Version: " + basemodule.__version__

    parser = argparse.ArgumentParser(**poptions)

    # Add standard arguments
    ## Should check that these have not been defined in argspec
    argspec.append(('-d','--defaults', {'help': 'Display help with info on default values', 'action': 'store_true'}, {}))
    argspec.append(('-q','--quiet',{'help': 'Quiet mode - only display/log errors', 'action': 'store_true'}, {}))

    # Special handling for "-d" to print default value info with help text
    defhelp = False
    if "-d" in sys.argv:
        defhelp = True
        pos = sys.argv.index("-d")
        sys.argv[pos] = "-h" # Set back to -h for argparse to recognise
        deffiles=[]
        defother=[]

    quiet = True if "-q" in sys.argv else False

# Process the supplied argument specs, add args to parser, store other info in arginfo
    arginfo = []
    for c,a in enumerate(argspec) :
        # Process all but last tuple entry as argparse arguments
        nonkwds = a[:-2]
        kwds = a[-2]
        parser.add_argument(*nonkwds, **kwds)
        # Create dict of framework keywords using argument name
        argn = nonkwds[-1] # Find the argument name from first 1 or 2 tuple entries
        if argn[0:2] == "--" : argn = argn[2:] # Will start with -- for options
        ainfo=a[-1]
        ainfo['name']=argn
        arginfo.append(ainfo)
        if defhelp:
            arg = nonkwds[0]
            if 'def' in ainfo:
                deffiles.append([arg,ainfo['def']])
            elif 'default' in kwds:
                defother.append([arg,kwds['default']])

# if -d specified, change the help epilog to info about argument defaults
    if defhelp:
        if not (deffiles or defother):
            deftext = "No defaults for parameters/options"
        else:
            deftext = "Defaults for parameters/options - see user docs for details\n"
        if deffiles:
            deftext = deftext + "\n  Font/file names\n"
            for (param,defv) in deffiles:
                deftext = deftext + '    {:<20}{}\n'.format(param,defv)
        if defother:
            deftext = deftext + "\n  Other parameters\n"
            for (param,defv) in defother:
                deftext = deftext + '    {:<20}{}\n'.format(param,defv)
        parser.epilog = deftext

# Parse the command-line arguments. If errors or -h used, procedure will exit here
    args = parser.parse_args()

# Process the argument values returned from argparse
    fppval = getattr(args,arginfo[0]['name'])
    if fppval is None : fppval = "" # For scripts that can be run with no positional parameters
    (fppath,fpbase,fpext)=_splitfn(fppval) # First pos param use for defaulting
    outfont = None
    infontlist = []

    for c,ainfo in enumerate(arginfo) :
        aval = getattr(args,ainfo['name'])
        atype = ainfo['type'] if 'type' in ainfo else None
        adef = ainfo['def'] if 'def' in ainfo else None
        if c == 0 :
            if aval[-1] in ("\\","/") : aval = aval[0:-1] # Remove trailing slashes
        else : #Handle defaults for all but first positional parameter
            if adef :
                if not aval : aval=""
                (apath,abase,aext)=_splitfn(aval)
                (dpath,dbase,dext)=_splitfn(adef) # dpath should be None
                if not apath :
                    if abase and aext :
                        apath = ""
                    else:
                        apath=fppath
                if not abase : abase = fpbase + dbase
                if not aext :
                    if dext :
                        aext = dext
                    elif (atype=='outfont' or atype=='infont') : aext = fpext
                aval = os.path.join(apath,abase+aext)
        # Open files/fonts
        if atype=='infont' :
            if tool is None:
                print "Can't specify a font without a font tool"
                sys.exit(1)
            infontlist.append((ainfo['name'],aval)) # Build list of fonts to open when other args processed
        elif atype=='infile' :
            if not quiet : print 'Opening file for input: ',aval
            try :
                aval=open(aval,"r")
            except Exception as e :
                print e
                sys.exit(1)
        elif atype=='outfile':
            if not quiet : print 'Opening file for output: ',aval
            try :
                aval=open(aval,"w")
            except Exception as e :
                print e
                sys.exit(1)
        elif atype=='outfont' :
            if tool is None:
                print "Can't specify a font without a font tool"
                sys.exit(1)
            outfont=aval # Can only be one outfont
            outfontext=aext
        elif atype=='optiondict' : # Turn multiple options in the form ['opt1=a','opt2=b'] into a dictionary
            avaldict={}
            if aval is not None:
                for option in aval:
                    x = option.split("=",1)
                    if len(x) <> 2 :
                        print "params must be of the form 'param=value'"
                        sys.exit(1)
                    if x[1] == "\\t" : x[1] = "\t" # Special handling for tab characters
                    avaldict[x[0]] = x[1]
            aval = avaldict

        setattr(args,ainfo['name'],aval)

# Create logger

    logfile = args.log if 'log' in args.__dict__ else None
    params = args.params if 'params' in args.__dict__ else {}
    loglevel = params['loglevel'].upper() if 'loglevel' in params else "W"
    scrlevel = params['scrlevel'].upper() if 'scrlevel' in params else "P"
    if quiet : scrlevel = "E"
    logger = loggerobj(logfile,loglevel=loglevel,scrlevel=scrlevel)
    setattr(args,'logger',logger)

# Open fonts - needs to be done after processing other arguments so logger and params are defined

    for name,aval in infontlist :
        if ff : aval=fontforge.open(aval)
        if psfu: aval=Ufont(aval, logger = logger)
        setattr(args,name,aval)
        # Process specific parameters for UFOlib fonts
        if psfu :
            font = aval
            params = args.params if 'params' in args.__dict__  else None
            if 'version' in args.__dict__ :
                if args.version : params["UFOversion"] = args.version
            for param in params:
                if param in font.outparams:
                    if param == "UFOversion" and params[param] not in ("2","3") : logger.log("UFO version must be 2 or 3", "S")
                    if param == "attribOrders" : logger.log("attribOrders can't be set by params", "S")
                    font.outparams[param] = params[param]
                elif param not in ('loglevel','scrlevel') : logger.log( "Parameter invalid: " + param, "S")

# All arguments processed, now call the main function
    result = fn(args)
    if outfont and result is not None:

        if ff:
            if not quiet : print "Saving font to " + outfont
            if outfontext=="ufo":
                result.generate(outfont)
            else : result.save(outfont)
        else: # Must be Pyslifont Ufont
            result.write(outfont)
    if logfile : logfile.close()

def _splitfn(fn): # Split filename into path, base and extension
    if fn : # Remove trailing slashes
        if fn[-1] in ("\\","/") : fn = fn[0:-1]
    (path,base) = os.path.split(fn)
    (base,ext) = os.path.splitext(base)
    return (path,base,ext)

