#!/usr/bin/env python
'General classes and functions for use in pysilfont scripts'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Raymond'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET
import re, sys, os, codecs, argparse

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

    def _protect(self, txt, base=_attribprotect) :
        return re.sub(ur'['+ur"".join(base.keys())+ur"]", lambda m: base[m.group(0)], txt)

    def _nsprotectattribs(self, attribs, localattribs, namespaces) :
        if attribs is not None :
            for k, v in attribs.items() :
                (lt, lq, lns) = self._localisens(k)
                if lns and lns not in namespaces :
                    namespaces[lns] = lq
                    localattribs['xmlns:'+lq] = lns
                localattribs[lt] = v

    def serialize_xml(self, write, base = None, indent = '', topns = True, namespaces = {}) :
        """Output the object using write() in a normalised way:
                topns if set puts all namespaces in root element else put them as low as possible"""
        if base is None :
            base = self.root
            write('<?xml version="1.0" encoding="UTF-8"?>\n')
            doctype=getattr(base, "doctype", "")
            if doctype <> "":
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
        
        for c in getattr(base, 'comments', []) :
            write(u'{}<!--{}-->\n'.format(indent, c))
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
                incr = self.indentFirst 
                self.indentFirst = self.indentIncr
                self.serialize_xml(write, base=b, indent=indent + incr, topns=topns, namespaces=namespaces.copy())
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
        for c in getattr(base, 'commentsafter', []) :
            write(u'{}<!--{}-->\n'.format(indent, c))

    def add_namespace(self, q, ns) :
        if ns in self.namespaces : return self.namespaces[ns]
        self.namespaces[ns] = q
        return q

class dirTree(dict) :
    """ An object to hold list of all files and directories in a directory
        with option to read sub-directory contents into dirTree objects.
        Iterates through readSub levels of subfolders """
    def __init__(self,dirn,readSub = 3) :
        for name in os.listdir(dirn) :
            item={}
            if os.path.isdir(os.path.join(dirn, name)) :
                item["type"] = "d"
                if readSub :
                    item["tree"] = dirTree(os.path.join(dirn,name),readSub-1)
            else :
                item["type"] = "f"
            self[name] = item
        
    def subTree(self,path) : # Returns dirTree object for a subtree based on subfolder name(s)
        # 'path' can be supplied as either a relative path (eg "subf/subsubf") or array (eg ['subf','subsubf']
        if type(path) is str : path = self._split(path)
        subf=path[0]
        if subf in self:
            if 'tree' in self[subf] :
                tree = self[subf]['tree']
            else :
                tree = ""
        else : return ""
        
        if len(path) == 1 :
            return tree
        else :
            path.pop(0)
            return tree.subTree(path)
        
    def _split(self,path) : # Turn a relative path into an array of subfolders
        npath = [os.path.split(path)[1]]
        while os.path.split(path)[0] :
            path = os.path.split(path)[0]
            npath.insert(0,os.path.split(path)[1])
        return npath

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
                sys.exit()
            for line in inxml.readlines() :
                self.inxmlstr = self.inxmlstr + line
            if parse :
                self.etree = ET.fromstring(self.inxmlstr)

    def write_to_xml(self,text) : # Used by ETWriter.serializeXML
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

def makeAttribOrder(attriblist) : # Turn a list of attrib names into an attributeOrder dict for ETWriter 
        return dict(map(lambda x:(x[1], x[0]), enumerate(attriblist)))
    

def execute(tool, fn, argspec) :
    # Function to handle parameter parsing, font and file opening etc in command-line scripts
    # Supports opening (and saving) fonts using FontForge (FF) or PysilFont UFOlib (PSFU).
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
    
    # Special handling for "-d" to print default value info with help text
    defhelp = False
    if "-d" in sys.argv:
        defhelp = True
        pos = sys.argv.index("-d")
        sys.argv[pos] = "-h" # Set back to -h for argparse to recognise
        deffiles=[]
        defother=[]
    if "-h" in sys.argv or "--help" in sys.argv: # Add extra argument to display in help text
        argspec.insert(0,('-d',{'help': 'Display help with info on default values', 'action': 'store_true'}, {}))

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
            deftext = "Defaults for parameters/options\n"
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
    
    for c,ainfo in enumerate(arginfo) :
        aval = getattr(args,ainfo['name'])
        atype = ainfo['type'] if 'type' in ainfo else None
        adef = ainfo['def'] if 'def' in ainfo else None
        if c <> 0 : #Handle defaults for all but first positional parameter
            if adef :
                if not aval : aval=""               
                (apath,abase,aext)=_splitfn(aval)
                (dpath,dbase,dext)=_splitfn(adef) # dpath should be None
                if not apath : apath=fppath
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
                sys.exit()
            print 'Opening font: ',aval
            try :
                if ff : aval=fontforge.open(aval)
                if psfu: aval=Ufont(aval)
            except Exception as e :
                print e
                sys.exit()
        elif atype=='infile' :
            print 'Opening file for input: ',aval
            try :
                aval=open(aval,"r")
            except Exception as e :
                print e
                sys.exit()
        elif atype=='outfile' :
            print 'Opening file for output: ',aval
            try :
                aval=open(aval,"w")
            except Exception as e :
                print e
                sys.exit()
        elif atype=='outfont' :
            if tool is None:
                print "Can't specify a font without a font tool"
                sys.exit() 
            outfont=aval # Can only be one outfont
            outfontext=aext
        elif atype=='optiondict' : # Turn multiple options in the form ['opt1=a','opt2=b'] into a dictionary
            avaldict={}
            if aval is not None:
                for option in aval:
                    x = option.split("=",1)
                    avaldict[x[0]] = x[1]
            aval = avaldict
        
        setattr(args,ainfo['name'],aval)

# All arguments processed, now call the main function
    result = fn(args)
    if outfont and result is not None:
        print "Saving font to " + outfont
        if ff:
            if outfontext=="ufo":
                result.generate(outfont)
            else : result.save(outfont)
        else: # Must be Pyslifont Ufont
            result.write(outfont)

def _splitfn(fn): # Split filename into path, base and extension
    (path,base) = os.path.split(fn)
    (base,ext) = os.path.splitext(base)
    return (path,base,ext)
    
