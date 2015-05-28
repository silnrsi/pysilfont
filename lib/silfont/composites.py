#!/usr/bin/env python
'Composite glyph definition'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.2'

import re
from xml.etree import ElementTree as ET

# REs to parse (from right to left) comment, SIL extention parameters, markinfo, UID, metrics,
# and (from left) glyph name

# Extract comment from end of line (NB: Doesn't use re.VERBOSE because it contains #.)
# beginning of line, optional whitespace, remainder, optional whitespace, comment to end of line
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

# REs to parse base and diacritic
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

# Parse metrics
lsb_rsb=re.compile(r"""^\s*                         # beginning of line, optional whitespace
    (?P<lsb>[-0-9]+)\s*(?:,\s*(?P<rsb>[-0-9]+))?    # optional metrics (either ^lsb,rsb or ^adv)
    \s*$""",re.VERBOSE)                             # optional whitespace, end of line

# RE to break off one key=value parameter from text inside [key=value;key=value;key=value]
paramdef=re.compile(r"""^\s*                # beginning of line, optional whitespace
    (?P<paramname>[a-z0-9]+)                # paramname
    \s*=\s*                                 # = (with optional white space before/after)
    (?P<paramval>[^;]+?)                    # any text up to ; or end of string
    \s*                                     # optional whitespace
    (?:;\s*(?P<rest>.+)$|\s*$)              # either ; and (non-empty) rest of parameters, or end of line
    """,re.VERBOSE)

class CompGlyph(object):

    def __init__(self, CDelement=None, CDline=None):
        self.CDelement = CDelement
        self.CDline = CDline

    def _parseparams(self, rest):
        """Parse a parameter line such as:
        key1=value1;key2=value2
        and return a dictionary with key:value pairs.
        """
        params = {}
        while rest:
            matchparam=re.match(paramdef,rest)
            if matchparam == None:
                raise ValueError('Parameter error: ' + rest)
            params[matchparam.group("paramname")] = matchparam.group("paramval")
            rest = matchparam.group("rest")
        return(params)

    def parsefromCDline(self):
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
        linetoparse = self.CDline
        errorfound = False
        line = re.sub('/_','_',linetoparse) # change /_ to _
        results = {}
        for parseinfo in initialtokens:
            if len(line) > 0:
                regex, groupname, missingiserror, errormsg = parseinfo
                matchresults = re.match(regex,line)
                if matchresults == None or (missingiserror and matchresults.group(groupname) == None):
                    raise ValueError(errormsg)
                line = matchresults.group('remainder')
                resultsval = matchresults.group(groupname)
                if resultsval != None:
                    results[groupname] = resultsval

# At this point results optionally may contain entries for any of 'commenttext', 'paraminfo', 'markinfo', 'UID', or 'metrics', 
# but it must have 'PSName' if any of 'paraminfo', 'markinfo', 'UID', or 'metrics' present
        note = results.pop('commenttext', None)
        if 'PSName' not in results:
            if len(results) > 0:
                raise ValueError("Missing glyph name")
            else: # comment only, or blank line
                return None
        dic = {}
        if 'paraminfo' in results:
            dic = self._parseparams(results.pop['paraminfo'])
        mark = results.pop('markinfo', None)
        if 'metrics' in results:
            m = results.pop('metrics')
            matchmetrics = re.match(lsb_rsb,m)
            if matchmetrics == None:
                raise ValueError('Error in parameters: ' + m)
            elif matchmetrics.group("rsb"):
                metricdic = {'lsb': matchmetrics.group('lsb'), 'rsb': matchmetrics.group('rsb')}
            else:
                metricdic = {'advance': matchmetrics.group('lsb')}
        else:
            metricdic = None

        # Create <glyph> element and assign attributes
        g = ET.Element('glyph',attrib=results)
        if note:                # note from commenttext becomes <note> subelement
            n = ET.SubElement(g,'note')
            n.text = note.rstrip()
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
                    raise ValueError("Error parsing glyph name: " + remainder)
                propdic = {}
                if matchresults.group('params'):
                    propdic = self._parseparams(matchresults.group('params'))
                # Create <base> subelement
                b = ET.SubElement(g, 'base', PSName=matchresults.group("basename"))
                if 'shift' in propdic:
                    x,y = propdic.pop('shift').split(',')
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
                    raise ValueError("Error parsing glyph name: " + remainder)
                propdic = {}
                if matchresults.group('params'):
                    propdic = self._parseparams(matchresults.group('params'))
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

        #if warningmsg:
        #    return "Warning: " + "; ".join(warningmsg), g
        self.CDelement = g

    def _diacinfo(self, node, parent, lastglyph):
        """receives attach element, PSName of its parent, PSName of most recent glyph
        returns a string equivalent of this node (and all its descendants)
        and a string with the name of the most recent glyph
        """
        diacname = node.get('PSName')
        atstring = node.get('at')
        withstring = node.get('with')
        propdic = {}
        if withstring != "_" + atstring:
            propdic['with'] = withstring
        subattachlist = []
        attachglyph = ""
        if parent != lastglyph:
            attachglyph = parent + ":"
        for subelement in node:
            if subelement.tag == 'property':
                propdic[subelement.get('name')] = subelement.get('value')
            elif subelement.tag == 'attach':
                subattachlist.append(subelement)
            elif subelement.tag == 'shift':
                propdic['shift'] = subelement.get('x') + ',' + subelement.get('y') 
            # else flag error/warning?
        propstring = ""
        if propdic:
            paramsep = " ["
            for k in propdic:
                propstring += paramsep + k + "=" + propdic[k]
                paramsep = ";"
            propstring += "]"
        returnstring = " + " + diacname + "@" + attachglyph + atstring + propstring
        prevglyph = diacname
        for s in subattachlist:
            string, prevglyph = self._diacinfo(s, diacname, prevglyph)
            returnstring += string
        return returnstring, prevglyph

    def _basediacinfo(self, baseelement):
        """receives base element and returns a string equivalent of this node (and all its desendants)"""
        basename = baseelement.get('PSName')
        returnstring = basename
        prevglyph = basename
        bpropdic = {}
        for child in baseelement:
            if child.tag == 'attach':
                string, prevglyph = self._diacinfo(child, basename, prevglyph)
                returnstring += string
            elif child.tag == 'shift':
                bpropdic['shift'] = child.get('x') + ',' + child.get('y') 
        if bpropdic:
            paramsep = " ["
            for k in bpropdic:
                returnstring += paramsep + k + "=" + bpropdic[k]
                paramsep = ";"
            returnstring += "]"

        return returnstring

    def parsefromCDelement(self):
        """Parse a glyph element such as:
        <glyph PSName="LtnSmITildeGraveDotBlw" UID="E000">
          <note>i tilde grave dot-below</note>
          <base PSName="LtnSmDotlessI">
            <attach PSName="CombDotBlw" at="L" with="_L" />
            <attach PSName="CombTilde" at="U" with="_U">
              <attach PSName="CombGrave" at="U" with="_U" />
            </attach>
          </base>
        </glyph>
        and produce the equivalent CDline in format:
        LtnSmITildeGraveDotBlw = LtnSmDotlessI + CombDotBlw@L + CombTilde@LtnSmDotlessI:U + CombGrave@U | E000 # i tilde grave dot-below
        """
        g = self.CDelement
        lsb = None
        rsb = None
        adv = None
        markinfo = None
        note = None
        paramdic = {}
        outputline = [g.get('PSName')]
        resultUID = g.get('UID')
        basesep = " = "

        for child in g:
            if child.tag == 'note':             note = child.text
            elif child.tag == 'property':
                if child.get('name') == 'mark': markinfo = child.get('value')
                else:                           paramdic[child.get('name')] = child.get('value')
            elif child.tag == 'lsb':            lsb = child.get('width')
            elif child.tag == 'rsb':            rsb = child.get('width')
            elif child.tag == 'advance':        adv = child.get('width')
            elif child.tag == 'base':
                outputline.extend([basesep, self._basediacinfo(child)])
                basesep = " _ "
        
        if adv:             outputline.extend([' ^', adv])
        if lsb and rsb:     outputline.extend([' ^', lsb, ',', rsb])
        if resultUID:       outputline.extend([' |', resultUID])
        if markinfo:        outputline.extend([' !', markinfo])
        if paramdic:
            paramsep = ' &['
            for k in paramdic:
                outputline.extend([paramsep, k, '=', paramdic[k]])
                paramsep = ';'
            outputline.append(']')
        if note:
            outputline.extend([' # ', note])
        self.CDline = "".join(outputline)

