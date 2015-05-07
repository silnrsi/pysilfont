#'parse composite definitions in XML format'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.1'

from xml.etree import ElementTree as ET

# ---------------------------------------------------------
# shiftinfo handles shift element (subelement of attach or base)
# ---------------------------------------------------------
def shiftinfo(s):
    """receives shift element and returns dictionary, for example
    <shift x="119" y="-110"/> returns {'shift':'119,-110'}
    """
    dic = {}
    dic['shift'] = s.get('x') + ',' + s.get('y')
    return dic

# ---------------------------------------------------------
# diacinfo handles attach element (and descendants)
# ---------------------------------------------------------
def diacinfo(node, parent, lastglyph):
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
            propdic.update(shiftinfo(subelement))
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
        string, prevglyph = diacinfo(s, diacname, prevglyph)
        returnstring += string
    return returnstring, prevglyph

# ---------------------------------------------------------
# basediacinfo handles base element (and descendants)
# ---------------------------------------------------------
def basediacinfo(baseelement):
    """receives base element and returns a string equivalent of this node (and all its desendants)"""
    
    basename = baseelement.get('PSName')
    returnstring = basename
    prevglyph = basename
    bpropdic = {}
    for child in baseelement:
        if child.tag == 'attach':
            string, prevglyph = diacinfo(child, basename, prevglyph)
            returnstring += string
        elif child.tag == 'shift':
            bpropdic.update(shiftinfo(child))
    if bpropdic:
        paramsep = " ["
        for k in bpropdic:
            returnstring += paramsep + k + "=" + bpropdic[k]
            paramsep = ";"
        returnstring += "]"

    return returnstring

# ---------------------------------------------------------
# parsecompxml handles glyph element (and descendants)
# ---------------------------------------------------------
def parsecompxml(g):
    """receives glyph element such as:
    <glyph PSName="LtnSmITildeGraveDotBlw" UID="E000">
      <note>i tilde grave dot-below</note>
      <base PSName="LtnSmDotlessI">
        <attach PSName="CombDotBlw" at="L" with="_L" />
        <attach PSName="CombTilde" at="U" with="_U">
          <attach PSName="CombGrave" at="U" with="_U" />
        </attach>
      </base>
    </glyph>
    and returns string in format:
    LtnSmITildeGraveDotBlw = LtnSmDotlessI + CombDotBlw@L + CombTilde@LtnSmDotlessI:U + CombGrave@U | E000 # i tilde grave dot-below
    """

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
            outputline.extend([basesep, basediacinfo(child)])
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
    return("".join(outputline))

# ---------------------------------------------------------

#'convert composite definition file from XML format by calling parsecompxml for each line in the input file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2015, SIL International  (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__author__ = 'David Rowe'
__version__ = '0.0.1'

from silfont.genlib import execute

# specify two parameters: input file (single line format), output file (XML format).
argspec = [
    ('input',{'help': 'Input file of CD in XML format'}, {'type': 'infile'}),
    ('output',{'help': 'Output file of CD in single line format'}, {'type': 'outfile'})]

def doit(args) :
    doctree = ET.parse(args.input)
    docroot = doctree.getroot()
    for g in docroot.findall('glyph'):
        args.output.write(parsecompxml(g)+'\n')
    return
    
execute(None,doit,argspec)
