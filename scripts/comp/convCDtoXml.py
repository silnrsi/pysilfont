#'parse composite definitions in RF format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.1'

import re
from xml.etree import ElementTree as ET

# ---------------------------------------------------------
# parsetoken used to break off glyph level parameters
# ---------------------------------------------------------
def parsetoken(regex,texttosearch,groupname,missingiserror=True):
    """
    parameters: 
        regular expression (needs to contain named group 'remainder')
        text to search
        groupname (usually name of named regex group (and also used as XML attribute tag))
        (optional) default True returns error if groupname is not present or is empty; override with False
    """
    matchresults = re.match(regex,texttosearch)
    if matchresults == None or (missingiserror and matchresults.group(groupname) == None):
        return (True, "", "")
    else:
        return (False, matchresults.group('remainder'), matchresults.group(groupname))

# ---------------------------------------------------------
# parseparams used to convert key=value parameters inside [] to dictionary
# ---------------------------------------------------------
def parseparams(rest):
    """Parse a parameter line such as:
    key1=value1;key2=value2
    and return a dictionary with key:value pairs.
    """

# RE to break off one key=value parameter from text
    paramdef=re.compile(r"""^\s*                # beginning of line, optional whitespace
        (?P<paramname>[a-z0-9]+)                # paramname
        \s*=\s*                                 # = (with optional white space before/after)
        (?P<paramval>[^;]+?)                    # any text up to ; or end of string
        \s*                                     # optional whitespace
        (?:;\s*(?P<rest>.+)$|\s*$)              # either ; and (non-empty) rest of parameters, or end of line
        """,re.VERBOSE)

    errorfound = False
    params = {}
    while errorfound == False and rest:
        matchparam=re.match(paramdef,rest)
        if matchparam == None:
            errorfound = True
        else:
            params[matchparam.group("paramname")] = matchparam.group("paramval")
            rest = matchparam.group("rest")
    if errorfound:
        return(None)
    else:
        return(params)

# ---------------------------------------------------------
# parsemetrics used to process lsb,rsb information
# ---------------------------------------------------------
def parsemetrics(m):

# Parse metrics
    lsb_rsb=re.compile(r"""^\s*                         # beginning of line, optional whitespace
        (?P<lsb>[-0-9]+)\s*(?:,\s*(?P<rsb>[-0-9]+))?    # optional metrics (either ^lsb,rsb or ^adv)
        \s*$""",re.VERBOSE)                             # optional whitespace, end of line

    matchmetrics = re.match(lsb_rsb,m)
    if matchmetrics == None:                            # should never happen!
        return None
    elif matchmetrics.group("rsb"):
        return {'lsb': matchmetrics.group('lsb'), 'rsb': matchmetrics.group('rsb')}
    else:
        return {'advance': matchmetrics.group('lsb')}

# ---------------------------------------------------------
# parsecompline handles a single line of composite definition text
# ---------------------------------------------------------
def parsecompline(linetoparse):
    """Parse a line of composite glyph information such as:
    LtnCapADiear = LtnCapA + CombDiaer@U |00C4 ! 1, 0, 0, 1 # comment
    and return a <glyph> element
    <glyph PSName="LtnCapADiear" UID="00C4" commenttext="comment" markinfo="1, 0, 0, 1">
      <base PSName="LtnCapA">
        <attach PSName="CombDiaer" at="U"/>
      </base>
    </glyph>
    Position info after @ can include optional base: (glyph name followed by colon).
    Return value is tuple: text message and None|<glyph> element.
    Any syntax error returns an error message and None.
    A valid line, returns "OK"|warning and <glyph> element. 
    A blank line or one with comment only returns "" and None.
    """

# ---------------------------------------------------------
# regular expressions to parse (from right to left)
# comment, SIL extention parameters, markinfo, UID, metrics,
# and (from left) glyph name
# ---------------------------------------------------------
# Parse input line with glyph information and/or comment.
#        NB: Doesn't use re.VERBOSE because it contains #.
#        beginning of line, optional whitespace, remainder, optional whitespace, comment to end of line
    inputline=re.compile(r"""^\s*(?P<remainder>.*?)(\s*#\s*(?P<commenttext>.*))?$""")

# Parse optional parameters (SIL extension) & [name=val,name=val]
    paraminfo=re.compile(r"""^\s*
        (?P<remainder>[^&]*?)
        \s*                                     # optional whitespace
        (?:&\s*\[(?P<paraminfo>[^]]*)\])?       # optional & [ paraminfo ]
        \s*$""",re.VERBOSE)                     # optional whitespace, end of line

# Parse markinfo
    markinfo=re.compile(r"""^\s*
        (?P<remainder>[^!]*?)
        \s*                                                 # optional whitespace
        (?:!\s*(?P<markinfo>[.0-9]+(?:,[ .0-9]+?){3}))?     # optional ! markinfo
        \s*$""",re.VERBOSE)                                 # optional whitespace, end of line

# Parse uid
    uidinfo=re.compile(r"""^\s*
        (?P<remainder>[^!]*?)
        \s*                                                 # optional whitespace
        (?:\|\s*(?P<UID>[0-9A-Za-z]{4,6}))?                 # optional | UID
        \s*$""",re.VERBOSE)                                 # optional whitespace, end of line

# Parse metrics
    metricsinfo=re.compile(r"""^\s*
        (?P<remainder>[^^]*?)
        \s*                                                 # optional whitespace
        (?:\^\s*(?P<metrics>[-0-9]+\s*(?:,\s*[-0-9]+)?))?   # optional metrics (either ^x,y or ^a)
        \s*$""",re.VERBOSE)                                 # optional whitespace, end of line

# Parse glyph information (up to =)
    glyphdef=re.compile(r"""^\s*                            # beginning of line, optional whitespace
        (?P<PSName>[.A-Za-z][._A-Za-z0-9]*)                 # glyphname
        \s*=\s*                                             # = (with optional white space before/after)
        (?P<remainder>.*?)                                  # remainder of line
        \s*$""",re.VERBOSE)                                 # optional whitespace, end of line

    # break tokens off the right hand side from right to left and finally off left hand side (up to =)
    initialtokens=[ (inputline,   'commenttext', False, ""),  
                    (paraminfo,   'paraminfo',   False, "Error parsing paramters after &:"),
                    (markinfo,    'markinfo',    False, "Error parsing information after ^"),
                    (uidinfo,     'UID',         False, "Error parsing information after |"),
                    (metricsinfo, 'metrics',     False, "Error parsing information after ^"),
                    (glyphdef,    'PSName',      True,  "Error parsing glyph name before =") ]

# ---------------------------------------------------------
# regular expressions to parse base and diacritic
# ---------------------------------------------------------
# Parse base information
    basedef=re.compile(r"""^\s*                             # beginning of line, optional whitespace
        (?P<basename>[.A-Za-z][._A-Za-z0-9]*)               # basename
        # position information is allowed but ignored (except to issue warning)
        (?:@                                                # optional position information preceded by @
        \s*                                                 # optional white space
        (?P<position>(?:[^ +_[])+)                          # optional position information preceded by @ (delimited by space + _ [ or end of line)
        \s*                                                 # optional whitespace
        )?                                                  # end of optional @ clause
        # end of position information
        \s*                                                 # optional whitespace
        (?:\[(?P<params>[^]]*)\])?                          # optional parameters
        \s*                                                 # optional whitespace
        (?P<remainder>.*)                                   # remainder of line
        $""",re.VERBOSE)                                    # end of line

# Parse diacritic information
    diacdef=re.compile(r"""^\s*                             # beginning of line, optional whitespace
        (?P<diacname>[.A-Za-z][._A-Za-z0-9]*)               # diacname
        (?:@                                                # optional position information preceded by @
        (?:(?:\s*(?P<base>[^: ]+)):)?                       # optional base glyph followed by :
        \s*                                                 # optional white space
        (?P<position>(?:[^ +_[])+)                          # optional position information preceded by @ (delimited by space + _ [ or end of line)
        \s*                                                 # optional whitespace
        )?                                                  # end of optional @ clause
        \s*                                                 # optional whitespace
        (?:\[(?P<params>[^]]*)\])?                          # optional parameters
        \s*                                                 # optional whitespace
        (?P<remainder>.*)                                   # remainder of line
        $""",re.VERBOSE)                                    # end of line

# ---------------------------------------------------------
# Begin processing line of text
# ---------------------------------------------------------
    errorfound = False
    line = re.sub('/_','_',linetoparse) # change /_ to _
    results = {}

    for parseinfo in initialtokens:
        if not errorfound and len(line) > 0:
            regex, groupname, flag, errormsg = parseinfo
            errorfound, line, returnval = parsetoken(regex, line, groupname, flag)
            if returnval:
                results[groupname] = returnval
    if errorfound:
        return errormsg, None

# At this point results optionally may contain entries for any of
# 'commenttext', 'paraminfo', 'markinfo', 'UID', or 'metrics', 
# but it must have 'PSName' if any of 'paraminfo', 'markinfo', 'UID', or 'metrics' present
    if 'PSName' not in results:
        if 'paraminfo' in results or 'markinfo' in results or 'UID' in results or 'metrics' in results:
            return "Missing glyph name", None
        else: # comment only, or blank line
            return "", None
    if 'commenttext' in results:
        note = results.pop('commenttext').rstrip()
    else:
        note = None
    dic = {}
    if 'paraminfo' in results:
        dic = parseparams(results['paraminfo'])
        if not dic:
            return "Error in parameter information: " + results['paraminfo'], None
        results.pop('paraminfo')
    if 'markinfo' in results:
        mark = results.pop('markinfo')
    else:
        mark = None
    if 'metrics' in results:
        metricdic = parsemetrics(results.pop('metrics'))
    else:
        metricdic = None

    # Create <glyph> element and assign attributes
    g = ET.Element('glyph',attrib=results)
    if note:                # note from commenttext becomes <note> subelement
        n = ET.SubElement(g,'note')
        n.text = note
    # markinfo becomes <property> subelement
    if mark:
        p = ET.SubElement(g, 'property', name = 'mark', value = mark)
    # paraminfo parameters (now in dic) become <property> subelements
    if dic:
        for key in dic:
            p = ET.SubElement(g, 'property', name = key, value = dic[key])
    # metrics parameters (now in metricdic) become subelements
    if metricdic:
        for key in metricdic:
            k = ET.SubElement(g, key, width=metricdic[key])

    # Prepare to parse remainder of line
    prevbase = None
    prevdiac = None
    remainder = line
    expectingbase = True
    expectingdiac = False
    warningmsg = []

    # top of loop to process remainder of line, breaking off base or diacritics from left to right
    while remainder != "" and (expectingbase or expectingdiac):
        if expectingbase:
            matchresults=re.match(basedef,remainder)
            if matchresults == None or matchresults.group("basename") == "" :
                return "Error parsing base glyph name: " + remainder, None
            propdic = {}
            if matchresults.group('params'):
                propdic = parseparams(matchresults.group('params'))
                if not propdic:
                    return "Error parsing parameters: " + matchresults.group('params'), None
            # Create <base> subelement
            b = ET.SubElement(g, 'base', PSName=matchresults.group("basename"))
            if 'shift' in propdic:
                x,y = tuple(propdic.pop('shift').split(','))
                shiftattr = {'x': x, 'y': y}
                s = ET.SubElement(b, 'shift', attrib=shiftattr)
            # parameters (now in propdic) become <property> subelements
            if propdic:
                for key in propdic:
                    p = ET.SubElement(b, 'property', name = key, value = propdic[key])
            if matchresults.group("position"):
                warningmsg += ["Position information on base glyph unsupported: @" + matchresults.group("position")]
            prevbase = b

        elif expectingdiac:
            matchresults=re.match(diacdef,remainder)
            if matchresults == None or matchresults.group("diacname") == "" :
                return "Error parsing diacritic glyph name: " + remainder, None
            propdic = {}
            if matchresults.group('params'):
                propdic = parseparams(matchresults.group('params'))
                if not propdic:
                    return "Error parsing parameters: " + matchresults.group('params'), None
            atval = matchresults.group("position")
            if 'with' in propdic:
                withval = propdic.pop('with')
            else:
                withval = "_" + atval
            # Because 'with' is Python reserved word, passing it directly as a parameter
            # causes Python syntax error, so build dictionary to pass to SubElement
            att = {'PSName': matchresults.group("diacname"), 'at': atval, 'with': withval}
            # Determine parent element, based on previous base and diacritic glyphs and optional
            # matchresults.group('base'), indicating diacritic attaches to a different glyph
            if matchresults.group('base') == None:
                if prevdiac != None:
                    parent = prevdiac
                else:
                    parent = prevbase
            elif matchresults.group('base') != prevbase.attrib['PSName']:
                return "Error in diacritic alternate base glyph: " + matchresults.group('base'), None
            else:
                parent = prevbase
                if prevdiac == None:
                    warningmsg += ["Unnecessary diacritic alternate base glyph: " + matchresults.group('base')]
            # Create <attach> subelement
            a = ET.SubElement(parent, 'attach', attrib=att)
            prevdiac = a
            if 'shift' in propdic:
                x,y = tuple(propdic.pop('shift').split(','))
                shiftattr = {'x': x, 'y': y}
                s = ET.SubElement(a, 'shift', attrib=shiftattr)
            if propdic:
                for key in propdic:
                    p = ET.SubElement(a, 'property', name = key, value = propdic[key])
        remainder = matchresults.group("remainder").lstrip()
        nextchar = remainder[:1]
        remainder = remainder[1:]
        expectingbase = nextchar == "_"
        expectingdiac = nextchar == "+"

    if warningmsg:
        return "Warning: " + "; ".join(warningmsg), g
    else:
        return "OK", g

# ---------------------------------------------------------

#'convert composite definition file to XML format by calling parsecompline for each line in the input file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.1'

# following two lines temporary
#import sys
#sys.path.insert(0,'/home/david/Src/pysilfont/lib')
# above two lines temporary
from silfont.genlib import execute

# specify three parameters: input file (single line format), output file (XML format), log file.
argspec = [
    ('input',{'help': 'Input file of CD in single line format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file of CD in XML format'}, {'type': 'outfile', 'def': '_out.xml'}),
    ('log',{'help': 'Log file'},{'type': 'outfile', 'def': '_log.txt'})]

def doit(args) :
    ifile = args.input
    ofile = args.output
    lfile = args.log
    f = ET.Element('font')
    for line in ifile.readlines():      ### could use enumerate() to get (zero-based) line number to include with errors
        e, g = parsecompline(line)
        if e == "OK" or e[:9] == "Warning: ":
            f.append(g)
        if e != "" and e != "OK":
            lfile.write(e+'\n')
    ofile.write(ET.tostring(f))     ### change to use normalised, nicely formatted output
    
    return
    
execute(None,doit,argspec)
