#!/usr/bin/env python
from __future__ import unicode_literals
'Composite glyph definition'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'

try:
    str = unicode
    chr = unichr
except NameError: # Will  occur with Python 3
    pass
import re
from xml.etree import ElementTree as ET

# REs to parse (from right to left) comment, SIL extention parameters, markinfo, UID, metrics,
# and (from left) glyph name

# Extract comment from end of line (NB: Doesn't use re.VERBOSE because it contains #.)
# beginning of line, optional whitespace, remainder, optional whitespace, comment to end of line
inputline=re.compile(r"""^\s*(?P<remainder>.*?)(\s*#\s*(?P<commenttext>.*))?$""")

# Parse SIL extension parameters in [...], but only after |
paraminfo=re.compile(r"""^\s*
    (?P<remainder>[^|]*
        ($|
        \|[^[]*$|
        \|[^[]*\[(?P<paraminfo>[^]]*)\]))
    \s*$""",re.VERBOSE)

# Parse markinfo
markinfo=re.compile(r"""^\s*
    (?P<remainder>[^!]*?)
    \s*
    (?:!\s*(?P<markinfo>[.0-9]+(?:,[ .0-9]+){3}))?      # ! markinfo
    (?P<remainder2>[^!]*?)
    \s*$""",re.VERBOSE)

# Parse uid
uidinfo=re.compile(r"""^\s*
    (?P<remainder>[^|]*?)
    \s*
    (?:\|\s*(?P<UID>[^^!]*)?)?                          # | follwed by nothing, or 4- to 6-digit UID 
    (?P<remainder2>[^|]*?)
    \s*$""",re.VERBOSE)

# Parse metrics
metricsinfo=re.compile(r"""^\s*
    (?P<remainder>[^^]*?)
    \s*
    (?:\^\s*(?P<metrics>[-0-9]+\s*(?:,\s*[-0-9]+)?))?   # metrics (either ^x,y or ^a)
    (?P<remainder2>[^^]*?)
    \s*$""",re.VERBOSE)

# Parse glyph information (up to =)
glyphdef=re.compile(r"""^\s*
    (?P<PSName>[._A-Za-z][._A-Za-z0-9-]*)               # glyphname
    \s*=\s*
    (?P<remainder>.*?)
    \s*$""",re.VERBOSE)

# break tokens off the right hand side from right to left and finally off left hand side (up to =)
initialtokens=[ (inputline,   'commenttext', ""),  
                (paraminfo,   'paraminfo',   "Error parsing parameters in [...]"),
                (markinfo,    'markinfo',    "Error parsing information after !"),
                (uidinfo,     'UID',         "Error parsing information after |"),
                (metricsinfo, 'metrics',     "Error parsing information after ^"),
                (glyphdef,    'PSName',      "Error parsing glyph name before =") ]

# Parse base and diacritic information
compdef=re.compile(r"""^\s*
    (?P<compname>[._A-Za-z][._A-Za-z0-9-]*)             # name of base or diacritic in composite definition
        (?:@                                            # @ preceeds position information
        (?:(?:\s*(?P<base>[^: ]+)):)?                   # optional base glyph followed by :
        \s*
        (?P<position>(?:[^ +&[])+)                      # position information (delimited by space + & [ or end of line)
        \s*)?                                           # end of @ clause
    \s*
    (?:\[(?P<params>[^]]*)\])?                          # parameters inside [..]
    \s*
    (?P<remainder>.*)$
    """,re.VERBOSE)

# Parse metrics
lsb_rsb=re.compile(r"""^\s*
    (?P<lsb>[-0-9]+)\s*(?:,\s*(?P<rsb>[-0-9]+))?        # optional metrics (either ^lsb,rsb or ^adv)
    \s*$""",re.VERBOSE)

# RE to break off one key=value parameter from text inside [key=value;key=value;key=value]
paramdef=re.compile(r"""^\s*
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
                raise ValueError("Parameter error: " + rest)
            params[matchparam.group('paramname')] = matchparam.group('paramval')
            rest = matchparam.group('rest')
        return(params)

    def parsefromCDline(self):
        """Parse the composite glyph information (in self.CDline) such as:
        LtnCapADiear = LtnCapA + CombDiaer@U |00C4 ! 1, 0, 0, 1 # comment
        and return a <glyph> element (in self.CDelement)
        <glyph PSName="LtnCapADiear" UID="00C4">
          <note>comment</note>
          <property name="mark" value="1, 0, 0, 1"/>
          <base PSName="LtnCapA">
            <attach PSName="CombDiaer" with="_U" at="U"/>
          </base>
        </glyph>
        Position info after @ can include optional base glyph name followed by colon.
        """
        line = self.CDline
        results = {}
        for parseinfo in initialtokens:
            if len(line) > 0:
                regex, groupname, errormsg = parseinfo
                matchresults = re.match(regex,line)
                if matchresults == None:
                    raise ValueError(errormsg)
                line = matchresults.group('remainder')
                resultsval = matchresults.group(groupname)
                if resultsval != None:
                    results[groupname] = resultsval.strip()
                    if groupname == 'paraminfo': # paraminfo match needs to be removed from remainder
                        line = line.rstrip('['+resultsval+']')
                if 'remainder2' in matchresults.groupdict().keys(): line += ' ' + matchresults.group('remainder2')
# At this point results optionally may contain entries for any of 'commenttext', 'paraminfo', 'markinfo', 'UID', or 'metrics', 
# but it must have 'PSName' if any of 'paraminfo', 'markinfo', 'UID', or 'metrics' present
        note = results.pop('commenttext', None)
        if 'PSName' not in results:
            if len(results) > 0:
                raise ValueError("Missing glyph name")
            else: # comment only, or blank line
                return None
        dic = {}
        UIDpresent = 'UID' in results
        if UIDpresent and results['UID'] == '':
            results.pop('UID')
        if 'paraminfo' in results:
            paramdata = results.pop('paraminfo')
            if UIDpresent:
                dic = self._parseparams(paramdata)
            else:
                line += " [" + paramdata + "]"
        mark = results.pop('markinfo', None)
        if 'metrics' in results:
            m = results.pop('metrics')
            matchmetrics = re.match(lsb_rsb,m)
            if matchmetrics == None:
                raise ValueError("Error in parameters: " + m)
            elif matchmetrics.group('rsb'):
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
        expectingdiac = False

        # top of loop to process remainder of line, breaking off base or diacritics from left to right
        while remainder != "":
            matchresults=re.match(compdef,remainder)
            if matchresults == None or matchresults.group('compname') == "" :
                raise ValueError("Error parsing glyph name: " + remainder)
            propdic = {}
            if matchresults.group('params'):
                propdic = self._parseparams(matchresults.group('params'))
            base = matchresults.group('base')
            position = matchresults.group('position')
            if expectingdiac:
                # Determine parent element, based on previous base and diacritic glyphs and optional
                # matchresults.group('base'), indicating diacritic attaches to a different glyph
                if base == None:
                    if prevdiac != None:
                        parent = prevdiac
                    else:
                        parent = prevbase
                elif base != prevbase.attrib['PSName']:
                    raise ValueError("Error in diacritic alternate base glyph: " + base)
                else:
                    parent = prevbase
                    if prevdiac == None:
                        raise ValueError("Unnecessary diacritic alternate base glyph: " + base)
                # Because 'with' is Python reserved word, passing it directly as a parameter
                # causes Python syntax error, so build dictionary to pass to SubElement
                att = {'PSName': matchresults.group('compname')}
                if position:
                    if 'with' in propdic:
                        withval = propdic.pop('with')
                    else:
                        withval = "_" + position
                    att['at'] = position
                    att['with'] = withval
                # Create <attach> subelement
                e = ET.SubElement(parent, 'attach', attrib=att)
                prevdiac = e
            elif (base or position):
                raise ValueError("Position information on base glyph not supported")
            else:
                # Create <base> subelement
                e = ET.SubElement(g, 'base', PSName=matchresults.group('compname'))
                prevbase = e
                prevdiac = None
            if 'shift' in propdic:
                xval, yval = propdic.pop('shift').split(',')
                s = ET.SubElement(e, 'shift', x=xval, y=yval)
            if 'scale' in propdic:
                xval, yval = propdic.pop('scale').split(',')
                s = ET.SubElement(e, 'scale', x=xval, y=yval)
            # whatever parameters are left in propdic become <property> subelements
            for key, val in propdic.items():
                p = ET.SubElement(e, 'property', name=key, value=val)

            remainder = matchresults.group('remainder').lstrip()
            nextchar = remainder[:1]
            remainder = remainder[1:].lstrip()
            expectingdiac = nextchar == '+'
            if nextchar == '&' or nextchar == '+':
                if len(remainder) == 0:
                    raise ValueError("Expecting glyph name after & or +")
            elif len(nextchar) > 0:
                raise ValueError("Expecting & or + and found " + nextchar)
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
                propdic['shift'] = subelement.get('x') + "," + subelement.get('y') 
            elif subelement.tag == 'scale':
                propdic['scale'] = subelement.get('x') + "," + subelement.get('y') 
            # else flag error/warning?
        propstring = ""
        if propdic:
            propstring += " [" + ";".join( [k + "=" + v for k,v in propdic.items()] ) + "]"
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
                bpropdic['shift'] = child.get('x') + "," + child.get('y') 
            elif child.tag == 'scale':
                bpropdic['scale'] = child.get('x') + "," + child.get('y') 
        if bpropdic:
            returnstring += " [" + ";".join( [k + "=" + v for k,v in bpropdic.items()] ) + "]"
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
                basesep = " & "

        if paramdic and resultUID == None:
            resultUID = " " # to force output of |
        if adv:             outputline.extend([' ^', adv])
        if lsb and rsb:     outputline.extend([' ^', lsb, ',', rsb])
        if resultUID:       outputline.extend([' |', resultUID])
        if markinfo:        outputline.extend([' !', markinfo])
        if paramdic:
            paramsep = " ["
            for k in paramdic:
                outputline.extend([paramsep, k, "=", paramdic[k]])
                paramsep = ";"
            outputline.append("]")
        if note:
            outputline.extend([" # ", note])
        self.CDline = "".join(outputline)

